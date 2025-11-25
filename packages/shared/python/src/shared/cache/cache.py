"""Cache interface and implementations."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Cache(ABC):
    """Abstract interface for caching operations."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass


class RedisCache(Cache):
    """Redis implementation of Cache."""

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        # In a real implementation, this would connect to Redis

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        # Mock implementation
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        # Mock implementation
        pass

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        # Mock implementation
        return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        # Mock implementation
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        # Mock implementation
        pass


class InMemoryCache(Cache):
    """In-memory implementation of Cache."""

    def __init__(self):
        """Initialize in-memory cache."""
        self._cache: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        self._cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return key in self._cache

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()


def create_cache(cache_type: str = "memory", **kwargs) -> Cache:
    """
    Factory function to create cache instances.

    Args:
        cache_type: Type of cache ("redis" or "memory")
        **kwargs: Additional arguments for cache initialization

    Returns:
        Cache instance
    """
    if cache_type == "redis":
        return RedisCache(**kwargs)
    elif cache_type == "memory":
        return InMemoryCache()
    else:
        raise ValueError(f"Unknown cache type: {cache_type}")
