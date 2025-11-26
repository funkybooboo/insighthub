"""SQL Database abstraction."""

from typing import Any, Optional
import psycopg2
import psycopg2.extras


class SqlDatabase:
    """Abstract SQL database interface."""

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> int:
        """Execute a query and return rows affected."""
        raise NotImplementedError

    def fetch_one(self, query: str, params: tuple[Any, ...] | None = None) -> Optional[dict[str, Any]]:
        """Fetch one row as a dictionary."""
        raise NotImplementedError

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        raise NotImplementedError

    def close(self) -> None:
        """Close the database connection."""
        raise NotImplementedError


class PostgresSqlDatabase(SqlDatabase):
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

    def fetch_one(self, query: str, params: tuple[Any, ...] | None = None) -> Optional[dict[str, Any]]:
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
