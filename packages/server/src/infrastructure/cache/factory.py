"""Cache infrastructure factory."""

from typing import Any, Optional
import time
from threading import Lock


class Cache:
    """Abstract cache interface."""

    def get(self, key: str) -> Any:
        """Get value from cache."""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all cache entries."""
        raise NotImplementedError


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
            if time.time() > entry['expires_at']:
                del self._cache[key]
                return None

            return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl

        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at
            }

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
            if time.time() > entry['expires_at']:
                del self._cache[key]
                return False

            return True

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()


class RedisCache(Cache):
    """Redis cache implementation."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0,
                 password: Optional[str] = None, default_ttl: int = 3600):
        try:
            import redis
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
            self._client.ping()  # Test connection
            self._available = True
        except (ImportError, Exception):
            self._client = None
            self._available = False

        self._default_ttl = default_ttl

    def get(self, key: str) -> Any:
        """Get value from cache."""
        if not self._available or not self._client:
            return None
        try:
            return self._client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        if not self._available or not self._client:
            return

        ttl = ttl or self._default_ttl
        try:
            self._client.setex(key, ttl, str(value))
        except Exception:
            pass

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._available or not self._client:
            return False
        try:
            return bool(self._client.delete(key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._available or not self._client:
            return False
        try:
            return bool(self._client.exists(key))
        except Exception:
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        if not self._available or not self._client:
            return
        try:
            self._client.flushdb()
        except Exception:
            pass


def create_cache(cache_type: str = "in_memory", **kwargs) -> Cache:
    """
    Factory function to create cache instances.

    Args:
        cache_type: Type of cache ("in_memory" or "redis")
        **kwargs: Additional arguments for cache initialization

    Returns:
        Cache instance
    """
    if cache_type == "redis":
        return RedisCache(**kwargs)
    else:
        return InMemoryCache(**kwargs)