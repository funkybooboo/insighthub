"""SQLite database implementation for development."""

import sqlite3
from typing import Any, Optional


class SqliteDatabase:
    """SQLite database implementation for development and testing."""

    def __init__(self, database_url: str):
        """Initialize SQLite database connection.

        Args:
            database_url: SQLite database URL (e.g., 'sqlite:///app.db')
        """
        # Extract database path from URL
        if database_url.startswith("sqlite:///"):
            db_path = database_url[10:]  # Remove 'sqlite:///'
        else:
            db_path = ":memory:"  # Default to in-memory database

        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row  # Return rows as dictionaries

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> int:
        """Execute a query and return rows affected."""
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self._connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()

    def fetch_one(
        self, query: str, params: tuple[Any, ...] | None = None
    ) -> Optional[dict[str, Any]]:
        """Fetch one row as a dictionary."""
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        cursor = self._connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            cursor.close()

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()