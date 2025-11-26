"""Cache infrastructure factory."""
from src.infrastructure.cache.cache import Cache
from src.infrastructure.cache.in_memory_cache import InMemoryCache
from src.infrastructure.cache.redis_cache import RedisCache


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
        # InMemoryCache only accepts default_ttl
        in_memory_kwargs = {}
        if "default_ttl" in kwargs:
            in_memory_kwargs["default_ttl"] = kwargs["default_ttl"]
        return InMemoryCache(**in_memory_kwargs)
