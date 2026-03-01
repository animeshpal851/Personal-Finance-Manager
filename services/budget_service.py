"""
Budget Service — set, retrieve, and monitor category budgets.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from database.mongo_connection import connection
from models.budget import Budget
from config import BUDGETS_COLLECTION, TRANSACTIONS_COLLECTION, BUDGET_ALERT_THRESHOLDS

logger = logging.getLogger(__name__)


class BudgetService:
    """Manages category budgets and threshold alerts."""

    def __init__(self):
        self._col = connection.get_collection(BUDGETS_COLLECTION)
        self._txn_col = connection.get_collection(TRANSACTIONS_COLLECTION)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def set_budget(self, budget: Budget) -> str:
        """
        Upsert a budget for (category, month, year).
        Returns the action taken: 'created' | 'updated'.
        """
        existing = self._col.find_one(
            {"category": budget.category, "month": budget.month, "year": budget.year}
        )
        if existing:
            self._col.update_one(
                {"_id": existing["_id"]},
                {"$set": {"limit_amount": budget.limit_amount}},
            )
            logger.info("Budget updated: %s", budget)
            return "updated"
        else:
            self._col.insert_one(budget.to_dict())
            logger.info("Budget created: %s", budget)
            return "created"

    def get_budgets_for_month(self, month: int, year: int) -> List[Budget]:
        """Return all budgets for a specific month/year."""
        docs = self._col.find({"month": month, "year": year})
        return [Budget.from_dict(d) for d in docs]

    def get_all_budgets(self) -> List[Budget]:
        """Return all stored budgets sorted by year/month."""
        docs = self._col.find({}).sort([("year", -1), ("month", -1)])
        return [Budget.from_dict(d) for d in docs]

    def delete_budget(self, category: str, month: int, year: int) -> bool:
        result = self._col.delete_one({"category": category, "month": month, "year": year})
        return result.deleted_count > 0

    # ------------------------------------------------------------------
    # Budget vs Actual Spending
    # ------------------------------------------------------------------

    def budget_vs_actual(self, month: int, year: int) -> List[Dict[str, Any]]:
        """
        Compare budgeted vs actual spending for each category in the given month.

        Returns a list of dicts with alert levels.
        """
        budgets = self.get_budgets_for_month(month, year)
        if not budgets:
            return []

        # Actual spend per category for the month
        start = datetime(year, month, 1)
        end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

        pipeline = [
            {
                "$match": {
                    "transaction_type": "expense",
                    "date": {"$gte": start, "$lt": end},
                }
            },
            {"$group": {"_id": "$category", "actual": {"$sum": "$amount"}}},
        ]
        actuals = {r["_id"]: r["actual"] for r in self._txn_col.aggregate(pipeline)}

        results = []
        for b in budgets:
            actual = actuals.get(b.category, 0.0)
            ratio = actual / b.limit_amount if b.limit_amount > 0 else 0.0
            alert = self._alert_level(ratio)
            results.append(
                {
                    "category": b.category,
                    "budget": b.limit_amount,
                    "actual": round(actual, 2),
                    "remaining": round(b.limit_amount - actual, 2),
                    "usage_pct": round(ratio * 100, 1),
                    "alert": alert,
                }
            )

        results.sort(key=lambda r: r["usage_pct"], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Threshold Alerts
    # ------------------------------------------------------------------

    def get_alerts(self, month: int, year: int) -> List[Dict[str, Any]]:
        """Return only budget entries that have triggered an alert (≥ 70%)."""
        data = self.budget_vs_actual(month, year)
        return [r for r in data if r["alert"] != "OK"]

    @staticmethod
    def _alert_level(ratio: float) -> str:
        if ratio >= BUDGET_ALERT_THRESHOLDS[2]:   # 100%
            return "🔴 EXCEEDED"
        if ratio >= BUDGET_ALERT_THRESHOLDS[1]:   # 90%
            return "🟠 CRITICAL"
        if ratio >= BUDGET_ALERT_THRESHOLDS[0]:   # 70%
            return "🟡 WARNING"
        return "OK"
