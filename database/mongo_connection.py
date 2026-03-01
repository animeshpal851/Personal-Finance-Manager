"""
MongoDB connection handler — singleton pattern.
"""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import MONGO_URI, DATABASE_NAME

logger = logging.getLogger(__name__)


class MongoConnection:
    """Thread-safe singleton MongoDB connection manager."""

    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> bool:
        """Establish connection to MongoDB. Returns True on success."""
        try:
            self._client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Force connection attempt
            self._client.admin.command("ping")
            self._db = self._client[DATABASE_NAME]
            logger.info("Connected to MongoDB: %s / %s", MONGO_URI, DATABASE_NAME)
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.error("MongoDB connection failed: %s", exc)
            raise ConnectionError(
                f"Cannot connect to MongoDB at {MONGO_URI}.\n"
                "Please ensure MongoDB is running and try again.\n"
                f"Details: {exc}"
            )

    def get_db(self):
        """Return the active database object."""
        if self._db is None:
            self.connect()
        return self._db

    def get_collection(self, name: str):
        """Return a named collection from the active database."""
        return self.get_db()[name]

    def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed.")


# Module-level singleton
connection = MongoConnection()
