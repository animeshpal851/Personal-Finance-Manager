"""
Report Service — MongoDB aggregation pipelines for financial summaries.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

from database.mongo_connection import connection
from config import TRANSACTIONS_COLLECTION

logger = logging.getLogger(__name__)


class ReportService:
    """Generates financial reports using MongoDB aggregation."""

    def __init__(self):
        self._col = connection.get_collection(TRANSACTIONS_COLLECTION)

    # ------------------------------------------------------------------
    # Monthly Income vs Expense
    # ------------------------------------------------------------------

    def monthly_summary(self) -> List[Dict[str, Any]]:
        """
        Aggregate total income and expense per calendar month.

        Returns a list of dicts:
          { year, month, total_income, total_expense, net_savings }
        sorted chronologically.
        """
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"},
                        "type": "$transaction_type",
                    },
                    "total": {"$sum": "$amount"},
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                    },
                    "amounts": {
                        "$push": {
                            "type": "$_id.type",
                            "total": "$total",
                        }
                    },
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]

        raw = list(self._col.aggregate(pipeline))
        results = []
        for doc in raw:
            income = next(
                (a["total"] for a in doc["amounts"] if a["type"] == "income"), 0.0
            )
            expense = next(
                (a["total"] for a in doc["amounts"] if a["type"] == "expense"), 0.0
            )
            results.append(
                {
                    "year": doc["_id"]["year"],
                    "month": doc["_id"]["month"],
                    "total_income": round(income, 2),
                    "total_expense": round(expense, 2),
                    "net_savings": round(income - expense, 2),
                }
            )
        return results

    # ------------------------------------------------------------------
    # Category-wise Expense Aggregation
    # ------------------------------------------------------------------

    def category_expense_summary(
        self,
        month: int = None,
        year: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Aggregate total expense by category.
        Optionally filter to a specific month/year.

        Returns: [{ category, total_expense, percentage }]  (sorted desc)
        """
        match_stage: Dict[str, Any] = {"transaction_type": "expense"}
        if month and year:
            start = datetime(year, month, 1)
            end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
            match_stage["date"] = {"$gte": start, "$lt": end}

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$category",
                    "total_expense": {"$sum": "$amount"},
                }
            },
            {"$sort": {"total_expense": -1}},
        ]

        raw = list(self._col.aggregate(pipeline))
        grand_total = sum(r["total_expense"] for r in raw) or 1.0
        return [
            {
                "category": r["_id"],
                "total_expense": round(r["total_expense"], 2),
                "percentage": round(r["total_expense"] / grand_total * 100, 1),
            }
            for r in raw
        ]

    # ------------------------------------------------------------------
    # Net Savings per Month
    # ------------------------------------------------------------------

    def net_savings_by_month(self) -> List[Dict[str, Any]]:
        """Return net_savings (income − expense) for every month on record."""
        return [
            {
                "year": r["year"],
                "month": r["month"],
                "net_savings": r["net_savings"],
                "total_income": r["total_income"],
                "total_expense": r["total_expense"],
            }
            for r in self.monthly_summary()
        ]

    # ------------------------------------------------------------------
    # Overall Totals
    # ------------------------------------------------------------------

    def overall_totals(self) -> Dict[str, float]:
        """Return grand total income, expense, and net savings across all time."""
        pipeline = [
            {
                "$group": {
                    "_id": "$transaction_type",
                    "total": {"$sum": "$amount"},
                }
            }
        ]
        raw = {r["_id"]: r["total"] for r in self._col.aggregate(pipeline)}
        income = raw.get("income", 0.0)
        expense = raw.get("expense", 0.0)
        return {
            "total_income": round(income, 2),
            "total_expense": round(expense, 2),
            "net_savings": round(income - expense, 2),
        }

    # ------------------------------------------------------------------
    # Per-category monthly expense (for anomaly detection)
    # ------------------------------------------------------------------

    def category_monthly_expenses(self, category: str) -> List[float]:
        """
        Return a list of monthly expense totals for a single category.
        Used by the analytics service for anomaly detection.
        """
        pipeline = [
            {"$match": {"transaction_type": "expense", "category": category}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"},
                    },
                    "total": {"$sum": "$amount"},
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]
        return [r["total"] for r in self._col.aggregate(pipeline)]

    def all_monthly_expense_by_category(self) -> Dict[str, List[float]]:
        """Return a dict of {category: [monthly_totals]} for all expense categories."""
        pipeline = [
            {"$match": {"transaction_type": "expense"}},
            {
                "$group": {
                    "_id": {
                        "category": "$category",
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"},
                    },
                    "total": {"$sum": "$amount"},
                }
            },
        ]
        raw = list(self._col.aggregate(pipeline))
        result: Dict[str, List[float]] = {}
        for r in raw:
            cat = r["_id"]["category"]
            result.setdefault(cat, []).append(r["total"])
        return result
