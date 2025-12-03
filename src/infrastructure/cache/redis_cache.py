from typing import Any, Optional, Protocol, cast

from src.infrastructure.cache.cache import Cache


class RedisClient(Protocol):
    """Protocol for Redis client interface."""

    def ping(self) -> object: ...
    def get(self, key: str) -> Optional[str]: ...
    def setex(self, key: str, time: int, value: str) -> object: ...
    def delete(self, key: str) -> int: ...
    def exists(self, key: str) -> int: ...
    def flushdb(self) -> object: ...


class RedisCache(Cache):
    """Redis cache implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600,
    ):
        self._client: Optional[RedisClient] = None
        try:
            import redis

            client = redis.Redis(
                host=host, port=port, db=db, password=password, decode_responses=True
            )
            client.ping()  # Test connection
            self._client = cast(RedisClient, client)
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
