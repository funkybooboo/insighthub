"""Redis-backed cache implementation."""

from __future__ import annotations

import json
from types import TracebackType
from typing import TYPE_CHECKING

from shared.logger import create_logger
from shared.types.common import JsonValue
from shared.types.option import Nothing, Option, Some

from .cache import Cache

if TYPE_CHECKING:
    from redis import Redis

logger = create_logger("redis-cache")

try:
    import redis as redis_lib

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis_lib = None


class RedisCache(Cache):
    """
    Redis-backed cache implementation.

    Provides persistent caching using Redis with automatic JSON serialization.

    Example:
        cache = RedisCache(host="localhost", port=6379, db=0)
        cache.set("user:123", {"name": "Alice"}, ttl=60)
        result = cache.get("user:123")
        if result.is_some():
            user = result.unwrap()
    """

    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        password: str | None = None,
        default_ttl: int | None = None,
    ) -> None:
        """
        Initialize Redis cache.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (optional)
            default_ttl: Default TTL in seconds (optional)
        """
        self._enabled = REDIS_AVAILABLE
        self._default_ttl = default_ttl
        self._client: Redis | None = None
        self._host = host
        self._port = port
        self._db = db
        self._password = password

        if self._enabled and redis_lib is not None:
            self._client = redis_lib.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
            )

    def _ensure(self) -> bool:
        """Ensure connection is available."""
        if not self._enabled or self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except Exception as e:
            logger.warning("Redis connection failed", error=str(e))
            return False

    def set(self, key: str, value: JsonValue, ttl: int | None = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to store (must be JSON-serializable)
            ttl: Time-to-live in seconds
        """
        if not self._ensure() or self._client is None:
            return
        payload = json.dumps(value)
        used_ttl = ttl if ttl is not None else self._default_ttl
        if used_ttl:
            self._client.setex(key, int(used_ttl), payload)
        else:
            self._client.set(key, payload)

    def get(self, key: str) -> Option[JsonValue]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Some(value) if found, Nothing() otherwise
        """
        if not self._ensure() or self._client is None:
            return Nothing()
        raw = self._client.get(key)
        if raw is None:
            return Nothing()
        try:
            decoded = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
            result: JsonValue = json.loads(decoded)
            return Some(result)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Nothing()

    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        if not self._ensure() or self._client is None:
            return
        self._client.delete(key)

    def clear(self) -> None:
        """Clear all values from the cache."""
        if not self._enabled or self._client is None:
            return
        self._client.flushdb()

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists
        """
        if not self._ensure() or self._client is None:
            return False
        return bool(self._client.exists(key))

    def __enter__(self) -> "RedisCache":
        """Context manager entry."""
        self._ensure()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        pass
