"""
Goal Service — savings goal creation, retrieval, and progress tracking.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from bson import ObjectId

from database.mongo_connection import connection
from config import GOALS_COLLECTION

logger = logging.getLogger(__name__)


class GoalService:
    """Tracks user-defined savings goals."""

    def __init__(self):
        self._col = connection.get_collection(GOALS_COLLECTION)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_goal(
        self,
        name: str,
        target_amount: float,
        deadline: Optional[datetime],
        current_amount: float = 0.0,
        notes: str = "",
    ) -> ObjectId:
        """Create a new savings goal and return its ObjectId."""
        doc = {
            "name": name.strip(),
            "target_amount": round(target_amount, 2),
            "current_amount": round(current_amount, 2),
            "deadline": deadline,
            "notes": notes.strip(),
            "created_at": datetime.utcnow(),
            "completed": False,
        }
        result = self._col.insert_one(doc)
        logger.info("Goal created: %s (id=%s)", name, result.inserted_id)
        return result.inserted_id

    def get_all_goals(self) -> List[Dict[str, Any]]:
        """Return all goals with progress metadata."""
        docs = list(self._col.find({}).sort("created_at", -1))
        return [self._enrich(d) for d in docs]

    def get_goal_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single goal by its string ID."""
        try:
            doc = self._col.find_one({"_id": ObjectId(goal_id)})
            return self._enrich(doc) if doc else None
        except Exception as exc:
            logger.warning("Invalid goal id %s: %s", goal_id, exc)
            return None

    def update_progress(self, goal_id: str, new_amount: float) -> bool:
        """Update the current_amount saved towards a goal."""
        try:
            oid = ObjectId(goal_id)
            doc = self._col.find_one({"_id": oid})
            if not doc:
                return False
            completed = new_amount >= doc["target_amount"]
            self._col.update_one(
                {"_id": oid},
                {"$set": {"current_amount": round(new_amount, 2), "completed": completed}},
            )
            logger.info("Goal %s updated to %.2f (completed=%s)", goal_id, new_amount, completed)
            return True
        except Exception as exc:
            logger.error("update_progress failed: %s", exc)
            return False

    def delete_goal(self, goal_id: str) -> bool:
        try:
            result = self._col.delete_one({"_id": ObjectId(goal_id)})
            return result.deleted_count > 0
        except Exception as exc:
            logger.error("delete_goal failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Progress enrichment
    # ------------------------------------------------------------------

    @staticmethod
    def _enrich(doc: dict) -> Dict[str, Any]:
        """Add computed progress fields to a goal document."""
        target = doc["target_amount"]
        current = doc["current_amount"]
        remaining = max(0.0, target - current)
        progress_pct = round(min(current / target * 100, 100), 1) if target else 0.0

        days_left = None
        monthly_required = None
        if doc.get("deadline"):
            delta = doc["deadline"] - datetime.utcnow()
            days_left = max(0, delta.days)
            months_left = max(1, days_left / 30)
            monthly_required = round(remaining / months_left, 2)

        return {
            "id": str(doc["_id"]),
            "name": doc["name"],
            "target_amount": target,
            "current_amount": current,
            "remaining": round(remaining, 2),
            "progress_pct": progress_pct,
            "deadline": doc.get("deadline"),
            "days_left": days_left,
            "monthly_required": monthly_required,
            "notes": doc.get("notes", ""),
            "completed": doc.get("completed", False),
            "created_at": doc.get("created_at"),
        }
