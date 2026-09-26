"""MongoDB Architecture Configuration Stub for NETORACLE.

This module prepares the architectural integration for MongoDB.
In accordance with Phase 1 guidelines:
- No live database connection is made.
- No database credentials are hardcoded.
- Prepared for asynchronous client integration (e.g., Motor / AsyncIOMotorClient)
  in subsequent phases when persistence is enabled.
"""

import logging
from typing import Any, Optional
from app.core.config import settings

logger = logging.getLogger("netoracle.db")


class MongoDBManager:
    """Manages MongoDB client lifecycle and database references."""

    def __init__(self) -> None:
        self.client: Optional[Any] = None
        self.db: Optional[Any] = None

    async def connect(self) -> None:
        """Architecture hook for connecting to MongoDB in future phases."""
        if settings.MONGODB_URI:
            logger.info("MongoDB URI detected. Live connection will be initialized in Phase 5.")
        else:
            logger.info("Phase 1: MongoDB integration prepared (in-memory/stub mode).")

    async def disconnect(self) -> None:
        """Architecture hook for disconnecting from MongoDB."""
        if self.client:
            logger.info("Closing MongoDB connection.")
            self.client = None
            self.db = None


db_manager = MongoDBManager()


def get_database() -> Optional[Any]:
    """Dependency injection helper for accessing MongoDB database instance."""
    return db_manager.db

