"""PostgreSQL database module - single database implementation."""

from typing import Any, Optional

import psycopg2
import psycopg2.extras

from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class DatabaseException(Exception):
    """Exception raised when database operations fail."""

    def __init__(self, message: str, operation: str, original_error: Optional[Exception] = None):
        """Initialize database exception.

        Args:
            message: Error message
            operation: Database operation that failed
            original_error: Original exception that was caught
        """
        self.message = message
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Database operation '{operation}' failed: {message}")


class SqlDatabase:
    """PostgreSQL database implementation."""

    def __init__(self, db_url: str):
        """
        Initialize PostgreSQL database connection.

        Args:
            db_url: PostgreSQL connection string

        Raises:
            DatabaseException: If connection fails
        """
        self.db_url = db_url
        try:
            self.conn = psycopg2.connect(db_url)
            self.conn.autocommit = True
            logger.debug("Database connection established")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseException(str(e), operation="connect", original_error=e) from e

    def execute(self, query: str, params: Optional[tuple[Any, ...]] = None) -> int:
        """Execute a query and return rows affected.

        Raises:
            DatabaseException: If the database operation fails
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount if cursor.rowcount else 0
        except psycopg2.Error as e:
            logger.error(f"Database execute failed: {e}")
            raise DatabaseException(str(e), operation="execute", original_error=e) from e
        except Exception as e:
            logger.error(f"Unexpected error during database execute: {e}")
            raise DatabaseException(str(e), operation="execute", original_error=e) from e

    def fetch_one(
        self, query: str, params: Optional[tuple[Any, ...]] = None
    ) -> Optional[dict[str, Any]]:
        """Fetch one row as a dictionary.

        Raises:
            DatabaseException: If the database operation fails
        """
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return dict(result) if result else None
        except psycopg2.Error as e:
            logger.error(f"Database fetch_one failed: {e}")
            raise DatabaseException(str(e), operation="fetch_one", original_error=e) from e
        except Exception as e:
            logger.error(f"Unexpected error during database fetch_one: {e}")
            raise DatabaseException(str(e), operation="fetch_one", original_error=e) from e

    def fetch_all(
        self, query: str, params: Optional[tuple[Any, ...]] = None
    ) -> list[dict[str, Any]]:
        """Fetch all rows as dictionaries.

        Raises:
            DatabaseException: If the database operation fails
        """
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Database fetch_all failed: {e}")
            raise DatabaseException(str(e), operation="fetch_all", original_error=e) from e
        except Exception as e:
            logger.error(f"Unexpected error during database fetch_all: {e}")
            raise DatabaseException(str(e), operation="fetch_all", original_error=e) from e

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            try:
                self.conn.close()
                logger.debug("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")


# Singleton instance (single-threaded application)
_db_instance: Optional[SqlDatabase] = None


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
        logger.info("Database connection initialized")
    return _db_instance


def close_sql_database() -> None:
    """
    Close the singleton PostgreSQL database connection.

    This should be called during application shutdown.
    """
    global _db_instance
    if _db_instance is not None:
        try:
            _db_instance.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
        finally:
            _db_instance = None
