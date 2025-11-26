"""SQL Database abstraction."""

from typing import Any, Optional


class SqlDatabase:
    """Abstract SQL database interface."""

    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> int:
        """Execute a query and return rows affected."""
        raise NotImplementedError

    def fetch_one(
        self, query: str, params: tuple[Any, ...] | None = None
    ) -> Optional[dict[str, Any]]:
        """Fetch one row as a dictionary."""
        raise NotImplementedError

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
        """Fetch all rows as dictionaries."""
        raise NotImplementedError

    def close(self) -> None:
        """Close the database connection."""
        raise NotImplementedError
