"""In-memory cache implementation."""

from __future__ import annotations

import fnmatch
import threading
import time
from types import TracebackType

from shared.types.common import JsonValue
from typing import Optional

from shared.types.common import JsonValue

from .cache import Cache


class InMemoryCache(Cache):
    """
    Thread-safe in-memory cache implementation.

    Useful for development, testing, and single-instance deployments
    where persistence is not required.

    Example:
        cache = InMemoryCache(default_ttl=300)  # 5 minute default TTL
        cache.set("user:123", {"name": "Alice"}, ttl=60)
        result = cache.get("user:123")
        if result is not None:
            user = result
    """

    def __init__(self, default_ttl: int | None = None) -> None:
        """
        Initialize in-memory cache.

        Args:
            default_ttl: Default time-to-live in seconds (None = no expiration)
        """
        self._data: dict[str, tuple[JsonValue, float | None]] = {}
        self._lock = threading.RLock()
        self._default_ttl = default_ttl

    def set(self, key: str, value: JsonValue, ttl: int | None = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (overrides default_ttl)
        """
        with self._lock:
            used_ttl = ttl if ttl is not None else self._default_ttl
            expiry: float | None = None
            if used_ttl is not None:
                expiry = time.time() + used_ttl
            self._data[key] = (value, expiry)

    def get(self, key: str) -> Optional[JsonValue]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Value if found and not expired, None otherwise
        """
        with self._lock:
            if key not in self._data:
                return None

            value, expiry = self._data[key]

            if expiry is not None and time.time() > expiry:
                del self._data[key]
                return None

            return value

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key: Cache key to delete
        """
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        """Clear all values from the cache."""
        with self._lock:
            self._data.clear()

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache and is not expired.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired
        """
        return self.get(key) is not None

    def keys(self, pattern: str = "*") -> list[str]:
        """
        Get all keys matching a pattern.

        Args:
            pattern: Simple glob pattern (* matches any characters)

        Returns:
            List of matching keys
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                k
                for k, (_, expiry) in self._data.items()
                if expiry is not None and current_time > expiry
            ]
            for k in expired_keys:
                del self._data[k]

            return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]

    def ttl(self, key: str) -> int | None:
        """
        Get remaining time-to-live for a key.

        Args:
            key: Cache key

        Returns:
            Remaining TTL in seconds, None if no expiry, -1 if key not found
        """
        with self._lock:
            if key not in self._data:
                return -1

            _, expiry = self._data[key]
            if expiry is None:
                return None

            remaining = int(expiry - time.time())
            if remaining <= 0:
                del self._data[key]
                return -1

            return remaining

    def __len__(self) -> int:
        """Return number of items in cache (including expired)."""
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.exists(key)

    def __enter__(self) -> "InMemoryCache":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        pass
