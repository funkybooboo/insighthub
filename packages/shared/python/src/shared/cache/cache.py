"""Abstract cache interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from shared.types.common import JsonValue


class Cache(ABC):
    """
    Abstract interface for cache implementations.

    Cache values must be JSON-serializable primitives or structures.
    """

    @abstractmethod
    def set(self, key: str, value: JsonValue, ttl: int | None = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (None = no expiration)
        """
        ...

    @abstractmethod
    def get(self, key: str) -> Optional[JsonValue]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Value if found and not expired, None otherwise
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key: Cache key to delete
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all values from the cache."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache and is not expired.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired
        """
        ...
