"""Factory for creating cache instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

from .cache import Cache
from .in_memory_cache import InMemoryCache
from .noop_cache import NoOpCache
from .redis_cache import RedisCache


class CacheType(Enum):
    """Enum for cache implementation types."""

    REDIS = "redis"
    IN_MEMORY = "in_memory"
    NOOP = "noop"


def create_cache(
    cache_type: str,
    host: str | None = None,
    port: int | None = None,
    db: int | None = None,
    password: str | None = None,
    default_ttl: int | None = None,
) -> Option[Cache]:
    """
    Create a cache instance based on configuration.

    Args:
        cache_type: Type of cache ("redis", "in_memory", "noop")
        host: Redis host (required for redis)
        port: Redis port (required for redis)
        db: Redis database number (required for redis)
        password: Redis password (optional)
        default_ttl: Default TTL in seconds (optional)

    Returns:
        Some(Cache) if creation succeeds, Nothing() if type unknown or params missing
    """
    try:
        cache_enum = CacheType(cache_type)
    except ValueError:
        return Nothing()

    if cache_enum == CacheType.REDIS:
        if host is None or port is None or db is None:
            return Nothing()
        return Some(
            RedisCache(
                host=host,
                port=port,
                db=db,
                password=password,
                default_ttl=default_ttl,
            )
        )
    elif cache_enum == CacheType.IN_MEMORY:
        return Some(InMemoryCache(default_ttl=default_ttl))
    elif cache_enum == CacheType.NOOP:
        return Some(NoOpCache())

    return Nothing()
