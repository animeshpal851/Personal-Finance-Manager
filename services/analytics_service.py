"""
Analytics Service — Financial Health Score & Expense Anomaly Detection.
Pure statistical calculations; no AI/ML libraries.
"""

import logging
from typing import Dict, List, Any

from services.report_service import ReportService
from services.budget_service import BudgetService
from utils.helpers import compute_mean, compute_std_dev, safe_divide
from config import ANOMALY_MULTIPLIER, HEALTH_SCORE_WEIGHTS

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Non-AI financial analytics engine."""

    def __init__(self):
        self._report = ReportService()
        self._budget = BudgetService()

    # ------------------------------------------------------------------
    # Financial Health Score (0–100)
    # ------------------------------------------------------------------

    def financial_health_score(self) -> Dict[str, Any]:
        """
        Compute a composite health score out of 100.

        Components:
        ┌─────────────────────┬────────────────────────────────────────┐
        │ Savings Rate (40pts)│ avg_savings / avg_income               │
        │ Budget Adherence    │ months under budget / total months     │
        │ (30pts)             │                                        │
        │ Expense Stability   │ 1 – (std_dev / mean) capped at 0      │
        │ (30pts)             │                                        │
        └─────────────────────┴────────────────────────────────────────┘
        """
        monthly = self._report.monthly_summary()
        if not monthly:
            return {"score": 0, "grade": "N/A", "breakdown": {}, "tips": []}

        incomes = [m["total_income"] for m in monthly]
        expenses = [m["total_expense"] for m in monthly]
        savings = [m["net_savings"] for m in monthly]

        avg_income = compute_mean(incomes)
        avg_expense = compute_mean(expenses)
        avg_savings = compute_mean(savings)

        # ── Component 1: Savings Rate ──────────────────────────────────
        savings_rate = safe_divide(avg_savings, avg_income)
        savings_rate = max(0.0, min(savings_rate, 1.0))          # clamp [0, 1]
        savings_score = round(savings_rate * HEALTH_SCORE_WEIGHTS["savings_rate"])

        # ── Component 2: Budget Adherence ─────────────────────────────
        months_within = sum(1 for m in monthly if m["total_expense"] <= m["total_income"])
        adherence_ratio = safe_divide(months_within, len(monthly))
        adherence_score = round(adherence_ratio * HEALTH_SCORE_WEIGHTS["budget_adherence"])

        # ── Component 3: Expense Stability ────────────────────────────
        std_dev = compute_std_dev(expenses)
        cv = safe_divide(std_dev, avg_expense)                   # coefficient of variation
        stability_ratio = max(0.0, 1.0 - cv)                     # lower CV → higher score
        stability_score = round(stability_ratio * HEALTH_SCORE_WEIGHTS["expense_stability"])

        total_score = savings_score + adherence_score + stability_score

        # ── Grade ─────────────────────────────────────────────────────
        grade = self._score_to_grade(total_score)

        # ── Actionable Tips ───────────────────────────────────────────
        tips = self._generate_tips(savings_rate, adherence_ratio, cv, monthly)

        return {
            "score": total_score,
            "grade": grade,
            "breakdown": {
                "savings_rate_pct": round(savings_rate * 100, 1),
                "savings_score": savings_score,
                "savings_score_max": HEALTH_SCORE_WEIGHTS["savings_rate"],
                "adherence_pct": round(adherence_ratio * 100, 1),
                "adherence_score": adherence_score,
                "adherence_score_max": HEALTH_SCORE_WEIGHTS["budget_adherence"],
                "expense_cv_pct": round(cv * 100, 1),
                "stability_score": stability_score,
                "stability_score_max": HEALTH_SCORE_WEIGHTS["expense_stability"],
            },
            "stats": {
                "avg_monthly_income": round(avg_income, 2),
                "avg_monthly_expense": round(avg_expense, 2),
                "avg_monthly_savings": round(avg_savings, 2),
                "months_analysed": len(monthly),
            },
            "tips": tips,
        }

    @staticmethod
    def _score_to_grade(score: int) -> str:
        if score >= 85:
            return "A  (Excellent)"
        if score >= 70:
            return "B  (Good)"
        if score >= 55:
            return "C  (Average)"
        if score >= 40:
            return "D  (Below Average)"
        return "F  (Needs Improvement)"

    @staticmethod
    def _generate_tips(
        savings_rate: float,
        adherence_ratio: float,
        cv: float,
        monthly: List[Dict],
    ) -> List[str]:
        tips = []
        if savings_rate < 0.20:
            tips.append("💡 Target saving ≥ 20% of income each month.")
        if adherence_ratio < 0.75:
            tips.append("💡 Spending exceeded income in many months — review fixed costs.")
        if cv > 0.30:
            tips.append("💡 Expenses vary widely; build an emergency fund for stability.")
        negative_months = sum(1 for m in monthly if m["net_savings"] < 0)
        if negative_months > 0:
            tips.append(
                f"💡 You had {negative_months} deficit month(s). "
                "Identify and cut discretionary spend."
            )
        if not tips:
            tips.append("✅ Your finances look healthy. Keep it up!")
        return tips

    # ------------------------------------------------------------------
    # Expense Anomaly Detection
    # ------------------------------------------------------------------

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Flag individual transactions whose amount is more than
        ANOMALY_MULTIPLIER × mean for that category.

        Algorithm:
          For each expense category:
            1. Compute mean of all historical transactions in that category.
            2. Flag transactions where amount > mean * ANOMALY_MULTIPLIER.

        Returns a list of anomaly records with context.
        """
        from database.mongo_connection import connection
        from config import TRANSACTIONS_COLLECTION

        col = connection.get_collection(TRANSACTIONS_COLLECTION)

        # Step 1: compute per-category mean
        pipeline_means = [
            {"$match": {"transaction_type": "expense"}},
            {"$group": {"_id": "$category", "mean": {"$avg": "$amount"}, "count": {"$sum": 1}}},
        ]
        category_stats = {
            r["_id"]: {"mean": r["mean"], "count": r["count"]}
            for r in col.aggregate(pipeline_means)
        }

        anomalies = []
        for category, stats in category_stats.items():
            if stats["count"] < 3:
                # Not enough data for meaningful anomaly detection
                continue
            threshold = stats["mean"] * ANOMALY_MULTIPLIER
            cursor = col.find(
                {
                    "transaction_type": "expense",
                    "category": category,
                    "amount": {"$gt": threshold},
                }
            ).sort("amount", -1)

            for doc in cursor:
                anomalies.append(
                    {
                        "id": str(doc["_id"]),
                        "date": doc["date"],
                        "category": category,
                        "amount": doc["amount"],
                        "description": doc.get("description", ""),
                        "category_mean": round(stats["mean"], 2),
                        "threshold": round(threshold, 2),
                        "deviation_pct": round(
                            (doc["amount"] - stats["mean"]) / stats["mean"] * 100, 1
                        ),
                    }
                )

        anomalies.sort(key=lambda a: a["deviation_pct"], reverse=True)
        return anomalies

    # ------------------------------------------------------------------
    # Savings Forecast (simple linear projection)
    # ------------------------------------------------------------------

    def savings_forecast(self, months_ahead: int = 6) -> Dict[str, Any]:
        """
        Project future savings using the average monthly savings rate.
        Simple linear projection: cumulative = current_balance + avg_savings * n
        """
        monthly = self._report.monthly_summary()
        if not monthly:
            return {"error": "Insufficient data for forecast."}

        savings_list = [m["net_savings"] for m in monthly]
        avg_savings = compute_mean(savings_list)
        current_total = sum(savings_list)
        std = compute_std_dev(savings_list)

        projections = []
        for n in range(1, months_ahead + 1):
            projected = current_total + avg_savings * n
            optimistic = current_total + (avg_savings + std) * n
            pessimistic = current_total + (avg_savings - std) * n
            projections.append(
                {
                    "month": n,
                    "projected": round(projected, 2),
                    "optimistic": round(optimistic, 2),
                    "pessimistic": round(pessimistic, 2),
                }
            )

        return {
            "current_total_savings": round(current_total, 2),
            "avg_monthly_savings": round(avg_savings, 2),
            "std_dev": round(std, 2),
            "projections": projections,
        }
