from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class SqlDatabase(ABC):
    """Abstract interface for SQL databases."""

    @abstractmethod
    def execute(self, query: str, params: Optional[dict] = None) -> None:
        """Execute a query that does not return results (INSERT, UPDATE, DELETE)."""
        pass

    @abstractmethod
    def fetchone(self, query: str, params: Optional[dict] = None) -> Optional[Dict[str, Any]]:
        """Execute a query and return a single row."""
        pass

    @abstractmethod
    def fetchall(self, query: str, params: Optional[dict] = None) -> List[Dict[str, Any]]:
        """Execute a query and return all rows."""
        pass

    @abstractmethod
    def execute_many(self, query: str, params_list: List[dict]) -> None:
        """Execute a query with multiple sets of parameters."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass
