"""PostgreSQL database module - single database implementation."""

from typing import Any, Optional

import psycopg2
import psycopg2.extras


class SqlDatabase:
    """PostgreSQL database implementation."""

    def __init__(self, db_url: str):
        """
        Initialize PostgreSQL database connection.

        Args:
            db_url: PostgreSQL connection string
        """
        self.db_url = db_url
        self.conn = psycopg2.connect(db_url)
        self.conn.autocommit = True

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> int:
        """Execute a query and return rows affected."""
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount if cursor.rowcount else 0

    def fetch_one(
        self, query: str, params: tuple[Any, ...] | None = None
    ) -> Optional[dict[str, Any]]:
        """Fetch one row as a dictionary."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()


# Singleton instance (single-threaded application)
_db_instance: SqlDatabase | None = None


def get_sql_database() -> SqlDatabase:
    """
    Get the singleton PostgreSQL database connection.

    Returns:
        SqlDatabase instance
    """
    global _db_instance
    if _db_instance is None:
        from src.config import config
        _db_instance = SqlDatabase(config.database_url)
    return _db_instance
