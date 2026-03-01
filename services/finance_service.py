"""
Finance Service — CRUD operations for transactions.
All DB interactions go through the database layer.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from bson import ObjectId

from database.mongo_connection import connection
from models.transaction import Transaction
from config import TRANSACTIONS_COLLECTION

logger = logging.getLogger(__name__)


class FinanceService:
    """Handles creation, retrieval, and deletion of transactions."""

    def __init__(self):
        self._col = connection.get_collection(TRANSACTIONS_COLLECTION)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def add_transaction(self, transaction: Transaction) -> ObjectId:
        """Insert a transaction document. Returns the new ObjectId."""
        doc = transaction.to_dict()
        result = self._col.insert_one(doc)
        logger.info("Transaction inserted: %s", result.inserted_id)
        return result.inserted_id

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_all_transactions(
        self,
        limit: int = 50,
        skip: int = 0,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Transaction]:
        """Fetch transactions with optional filtering."""
        query: Dict[str, Any] = {}

        if transaction_type:
            query["transaction_type"] = transaction_type.lower()
        if category:
            query["category"] = {"$regex": category, "$options": "i"}
        if start_date or end_date:
            date_filter: Dict[str, datetime] = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["date"] = date_filter

        cursor = (
            self._col.find(query)
            .sort("date", -1)
            .skip(skip)
            .limit(limit)
        )
        return [Transaction.from_dict(doc) for doc in cursor]

    def get_transaction_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Fetch a single transaction by its string ID."""
        try:
            doc = self._col.find_one({"_id": ObjectId(transaction_id)})
            return Transaction.from_dict(doc) if doc else None
        except Exception as exc:
            logger.warning("Invalid transaction id %s: %s", transaction_id, exc)
            return None

    def get_transactions_by_month(self, month: int, year: int) -> List[Transaction]:
        """Return all transactions for a specific calendar month."""
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        query = {"date": {"$gte": start, "$lt": end}}
        return [Transaction.from_dict(d) for d in self._col.find(query).sort("date", 1)]

    def count_transactions(self) -> int:
        """Total number of stored transactions."""
        return self._col.count_documents({})

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction by ID. Returns True if deleted."""
        try:
            result = self._col.delete_one({"_id": ObjectId(transaction_id)})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info("Deleted transaction %s", transaction_id)
            return deleted
        except Exception as exc:
            logger.error("Delete failed for %s: %s", transaction_id, exc)
            return False

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_distinct_categories(self, transaction_type: Optional[str] = None) -> List[str]:
        """Return all unique categories stored in the DB."""
        query = {}
        if transaction_type:
            query["transaction_type"] = transaction_type.lower()
        return self._col.distinct("category", query)

    def get_date_range(self) -> Dict[str, Optional[datetime]]:
        """Return the earliest and latest transaction dates."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "min_date": {"$min": "$date"},
                    "max_date": {"$max": "$date"},
                }
            }
        ]
        result = list(self._col.aggregate(pipeline))
        if result:
            return {"min": result[0]["min_date"], "max": result[0]["max_date"]}
        return {"min": None, "max": None}
