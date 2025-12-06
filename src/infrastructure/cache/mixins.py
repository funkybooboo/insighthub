"""Cache mixin utilities for services."""

import json
from datetime import datetime
from typing import Optional, TypeVar

from src.infrastructure.cache.cache import Cache

T = TypeVar("T")


class CacheMixin:
    """Mixin providing common caching operations for services."""

    cache: Optional[Cache] = None

    def _cache_object(self, key: str, data: dict, ttl: int = 300) -> None:
        """Cache an object as JSON.

        Args:
            key: Cache key
            data: Data dictionary to cache
            ttl: Time-to-live in seconds (default 5 minutes)
        """
        if not self.cache:
            return
        value = json.dumps(data)
        self.cache.set(key, value, ttl=ttl)

    def _get_cached_object(self, key: str) -> Optional[dict]:
        """Get cached object from JSON.

        Args:
            key: Cache key

        Returns:
            Cached data dictionary or None
        """
        if not self.cache:
            return None
        cached = self.cache.get(key)
        if not cached:
            return None
        try:
            return json.loads(cached)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _invalidate_cache(self, key: str) -> None:
        """Invalidate cache entry.

        Args:
            key: Cache key
        """
        if not self.cache:
            return
        self.cache.delete(key)

    @staticmethod
    def _serialize_datetime(dt: datetime) -> str:
        """Serialize datetime to ISO format."""
        return dt.isoformat()

    @staticmethod
    def _deserialize_datetime(dt_str: str) -> datetime:
        """Deserialize datetime from ISO format."""
        return datetime.fromisoformat(dt_str)
