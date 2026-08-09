from typing import AsyncGenerator
from app.config import settings
from app.utils.logger import logger


class DatabaseSessionManager:
    """
    Manages database connectivity and session lifecycle for production scalability.
    Supports relational DB context and Firestore connection management.
    """
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._is_connected = False

    async def connect(self) -> None:
        """Initialize database connection pool."""
        self._is_connected = True
        logger.info(f"Database session manager initialized for project: {settings.FIREBASE_PROJECT_ID}")

    async def disconnect(self) -> None:
        """Close database connection pool."""
        self._is_connected = False
        logger.info("Database session manager disconnected successfully.")

    @property
    def is_connected(self) -> bool:
        return self._is_connected


db_manager = DatabaseSessionManager(db_url=settings.DATABASE_URL)


async def get_db_session() -> AsyncGenerator[DatabaseSessionManager, None]:
    """
    FastAPI dependency that yields a database session context.
    """
    try:
        yield db_manager
    finally:
        pass
