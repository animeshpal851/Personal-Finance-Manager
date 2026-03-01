"""
User model — placeholder for future multi-user support.
"""

from datetime import datetime
from typing import Optional
from bson import ObjectId


class User:
    """Represents an application user (reserved for future multi-user expansion)."""

    def __init__(
        self,
        username: str,
        email: str,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
    ):
        self._id = _id
        self.username = username.strip()
        self.email = email.strip().lower()
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> dict:
        doc = {
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
        }
        if self._id:
            doc["_id"] = self._id
        return doc

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            _id=data.get("_id"),
            username=data["username"],
            email=data["email"],
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        return f"User(username={self.username}, email={self.email})"
