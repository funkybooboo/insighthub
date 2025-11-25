"""PostgreSQL implementation of the SqlDatabase interface."""

from typing import Any, Dict, List, Optional

from .postgres import PostgresConnection, PostgresDatabase
from .sql_database import SqlDatabase


class PostgresSqlDatabase(SqlDatabase):
    """PostgreSQL implementation of the SqlDatabase interface."""

    def __init__(self, db_url: str):
        """
        Initialize the PostgreSQL database.

        Args:
            db_url: The database connection URL.
        """
        self.connection = PostgresConnection(db_url)
        self.db = PostgresDatabase(self.connection)

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Execute a query that does not return results (INSERT, UPDATE, DELETE)."""
        self.db.execute(query, params, commit=True)

    def fetchone(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single row."""
        return self.db.fetchone(query, params)

    def fetchall(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return all rows."""
        return self.db.fetchall(query, params)

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        """Execute a query with multiple sets of parameters."""
        self.db.execute_many(query, params_list)

    def close(self) -> None:
        """Close the database connection."""
        self.db.close()
