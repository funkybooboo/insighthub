
import time
from threading import Lock
from typing import Any, Optional

from src.infrastructure.cache.cache import Cache


class InMemoryCache(Cache):
    """Simple in-memory cache implementation."""

    def __init__(self, default_ttl: int = 3600):
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = default_ttl
        self._lock = Lock()

    def get(self, key: str) -> Any:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return None

            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl

        with self._lock:
            self._cache[key] = {"value": value, "expires_at": expires_at}

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            if key not in self._cache:
                return False

            entry = self._cache[key]
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                return False

            return True

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
