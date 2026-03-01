"""
Budget model — category-level monthly spending limit.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId


class Budget:
    """Represents a budget allocation for a category in a given month/year."""

    def __init__(
        self,
        category: str,
        limit_amount: float,
        month: int,
        year: int,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
    ):
        self._id = _id
        self.category = category
        self.limit_amount = round(float(limit_amount), 2)
        self.month = month
        self.year = year
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        doc = {
            "category": self.category,
            "limit_amount": self.limit_amount,
            "month": self.month,
            "year": self.year,
            "created_at": self.created_at,
        }
        if self._id:
            doc["_id"] = self._id
        return doc

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        return cls(
            _id=data.get("_id"),
            category=data["category"],
            limit_amount=data["limit_amount"],
            month=data["month"],
            year=data["year"],
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        return (
            f"Budget(category={self.category}, limit={self.limit_amount}, "
            f"period={self.month}/{self.year})"
        )
