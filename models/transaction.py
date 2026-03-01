"""
Transaction model — represents a single income or expense entry.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId


class Transaction:
    """Represents a financial transaction (income or expense)."""

    def __init__(
        self,
        date: datetime,
        transaction_type: str,   # "income" | "expense"
        category: str,
        amount: float,
        description: str = "",
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
    ):
        self._id = _id
        self.date = date
        self.transaction_type = transaction_type.lower()
        self.category = category
        self.amount = round(float(amount), 2)
        self.description = description.strip()
        self.created_at = created_at or datetime.utcnow()

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Convert to a MongoDB-ready dictionary."""
        doc = {
            "date": self.date,
            "transaction_type": self.transaction_type,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "created_at": self.created_at,
        }
        if self._id:
            doc["_id"] = self._id
        return doc

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Construct a Transaction from a MongoDB document."""
        return cls(
            _id=data.get("_id"),
            date=data["date"],
            transaction_type=data["transaction_type"],
            category=data["category"],
            amount=data["amount"],
            description=data.get("description", ""),
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        return (
            f"Transaction(type={self.transaction_type}, "
            f"category={self.category}, amount={self.amount}, "
            f"date={self.date.strftime('%Y-%m-%d')})"
        )
