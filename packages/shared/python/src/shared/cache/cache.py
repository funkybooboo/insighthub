"""Lightweight Redis-backed cache shared library."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class Cache(ABC):
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        ...

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear the cache."""
        ...
