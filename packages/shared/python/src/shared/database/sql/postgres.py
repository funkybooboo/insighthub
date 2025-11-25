"""PostgreSQL database interface using psycopg2."""

from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresConnection:
    """Manages a connection to a PostgreSQL database."""

    def __init__(self, db_url: str):
        """
        Initialize the connection.

        Args:
            db_url: The database connection URL.
        """
        self.db_url = db_url
        self.connection = None

    def connect(self):
        """Connect to the database."""
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(self.db_url)

    def close(self):
        """Close the database connection."""
        if self.connection and not self.connection.closed:
            self.connection.close()

    def commit(self):
        """Commit the current transaction."""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Rollback the current transaction."""
        if self.connection:
            self.connection.rollback()
    def get_cursor(self, as_dict: bool = False):
        """
        Get a cursor for the current connection.

        Args:
            as_dict: Whether to return results as dictionaries.

        Returns:
            A cursor object.
        """
        self.connect()
        if as_dict:
            return self.connection.cursor(cursor_factory=RealDictCursor)
        return self.connection.cursor()


class PostgresDatabase:
    """A wrapper around a PostgreSQL connection that provides methods for executing queries."""

    def __init__(self, connection: PostgresConnection):
        """
        Initialize the database.

        Args:
            connection: A PostgresConnection object.
        """
        self.connection = connection

    def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None, commit: bool = False
    ) -> None:
        """
        Execute a SQL query.

        Args:
            query: The SQL query to execute.
            params: The parameters to use with the query.
            commit: Whether to commit the transaction.
        """
        cursor = self.connection.get_cursor()
        cursor.execute(query, params)
        if commit:
            self.connection.connection.commit()
        cursor.close()

    def fetchall(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and fetch all results.

        Args:
            query: The SQL query to execute.
            params: The parameters to use with the query.

        Returns:
            A list of dictionaries representing the rows.
        """
        cursor = self.connection.get_cursor(as_dict=True)
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results

    def fetchone(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a SQL query and fetch one result.

        Args:
            query: The SQL query to execute.
            params: The parameters to use with the query.

        Returns:
            A dictionary representing the row, or None if no results are found.
        """
        cursor = self.connection.get_cursor(as_dict=True)
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        """Execute a query with multiple sets of parameters."""
        cursor = self.connection.get_cursor()
        cursor.executemany(query, params_list)
        self.connection.connection.commit()
        cursor.close()

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()
