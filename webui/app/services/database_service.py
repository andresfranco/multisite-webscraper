"""
Database Service
================
Service module for database operations and session management.
"""

from contextlib import contextmanager
from typing import Optional
from sqlalchemy.orm import Session

from webscraper_core.database import create_connection, create_tables


class DatabaseService:
    """Service for managing database connections and sessions."""

    def __init__(self, db_path: str):
        """
        Initialize DatabaseService.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.SessionLocal = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize database connection and create tables."""
        self.SessionLocal = create_connection(self.db_path)
        if self.SessionLocal is None:
            raise RuntimeError(
                f"Failed to create database connection to {self.db_path}"
            )
        create_tables()

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            Session: SQLAlchemy session object

        Raises:
            RuntimeError: If session factory is not initialized
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """
        Context manager for database session.
        Automatically handles session cleanup.

        Yields:
            Session: SQLAlchemy session object
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Close database connection."""
        if self.SessionLocal is not None:
            # SQLAlchemy sessions don't need explicit closure for the factory
            pass
