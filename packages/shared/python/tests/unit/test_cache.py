"""
Behavior tests for Cache implementations.

These tests verify the Cache interface implementations (InMemoryCache, NoOpCache)
provide consistent caching behavior for key-value storage operations.
"""

import time

import pytest

from shared.cache.factory import CacheType, create_cache
from shared.cache.in_memory_cache import InMemoryCache
from shared.cache.noop_cache import NoOpCache


class TestInMemoryCacheBehavior:
    """Test InMemoryCache input/output behavior."""

    def test_set_and_get_returns_value(self) -> None:
        """Setting a value and getting it returns the same value."""
        cache = InMemoryCache()
        cache.set("key", "value")

        result = cache.get("key")

        assert result is not None
        assert result == "value"

    def test_get_nonexistent_key_returns_nothing(self) -> None:
        """Getting a nonexistent key returns None."""
        cache = InMemoryCache()

        result = cache.get("nonexistent")

        assert result is None

    def test_set_overwrites_existing_value(self) -> None:
        """Setting a key that already exists overwrites the value."""
        cache = InMemoryCache()
        cache.set("key", "first")
        cache.set("key", "second")

        result = cache.get("key")

        assert result == "second"

    def test_delete_removes_key(self) -> None:
        """Deleting a key removes it from the cache."""
        cache = InMemoryCache()
        cache.set("key", "value")
        cache.delete("key")

        result = cache.get("key")

        assert result is None

    def test_delete_nonexistent_key_is_noop(self) -> None:
        """Deleting a nonexistent key does not raise an error."""
        cache = InMemoryCache()

        # Should not raise
        cache.delete("nonexistent")

    def test_clear_removes_all_keys(self) -> None:
        """Clearing the cache removes all stored values."""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_exists_returns_true_for_existing_key(self) -> None:
        """Checking existence of existing key returns True."""
        cache = InMemoryCache()
        cache.set("key", "value")

        assert cache.exists("key") is True

    def test_exists_returns_false_for_nonexistent_key(self) -> None:
        """Checking existence of nonexistent key returns False."""
        cache = InMemoryCache()

        assert cache.exists("nonexistent") is False

    def test_contains_operator(self) -> None:
        """The 'in' operator works for checking key existence."""
        cache = InMemoryCache()
        cache.set("key", "value")

        assert "key" in cache
        assert "nonexistent" not in cache

    def test_len_returns_item_count(self) -> None:
        """Length returns the number of items in cache."""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        assert len(cache) == 2


class TestInMemoryCacheTTL:
    """Test InMemoryCache TTL (time-to-live) behavior."""

    def test_ttl_expires_value(self) -> None:
        """Values expire after TTL seconds."""
        cache = InMemoryCache()
        cache.set("key", "value", ttl=1)

        # Should exist immediately
        assert cache.get("key") is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key") is None

    def test_default_ttl_applies_to_all_keys(self) -> None:
        """Default TTL is applied when not specified per-key."""
        cache = InMemoryCache(default_ttl=1)
        cache.set("key", "value")

        # Should exist immediately
        assert cache.get("key") is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("key") is None

    def test_per_key_ttl_overrides_default(self) -> None:
        """Per-key TTL overrides the default TTL."""
        cache = InMemoryCache(default_ttl=10)
        cache.set("key", "value", ttl=1)

        time.sleep(1.1)

        assert cache.get("key") is None

    def test_no_ttl_means_no_expiration(self) -> None:
        """Values without TTL do not expire."""
        cache = InMemoryCache()
        cache.set("key", "value")

        # Should persist
        assert cache.get("key") is not None

    def test_ttl_method_returns_remaining_time(self) -> None:
        """TTL method returns remaining seconds until expiration."""
        cache = InMemoryCache()
        cache.set("key", "value", ttl=10)

        remaining = cache.ttl("key")

        assert remaining is not None
        assert remaining > 0
        assert remaining <= 10

    def test_ttl_returns_none_for_no_expiry(self) -> None:
        """TTL method returns None for keys without expiration."""
        cache = InMemoryCache()
        cache.set("key", "value")

        assert cache.ttl("key") is None

    def test_ttl_returns_negative_for_nonexistent_key(self) -> None:
        """TTL method returns -1 for nonexistent keys."""
        cache = InMemoryCache()

        assert cache.ttl("nonexistent") == -1

    def test_exists_returns_false_for_expired_key(self) -> None:
        """Existence check returns False for expired keys."""
        cache = InMemoryCache()
        cache.set("key", "value", ttl=1)

        time.sleep(1.1)

        assert cache.exists("key") is False


class TestInMemoryCacheKeys:
    """Test InMemoryCache key listing and patterns."""

    def test_keys_returns_all_keys(self) -> None:
        """Keys method returns all stored keys."""
        cache = InMemoryCache()
        cache.set("user:1", "alice")
        cache.set("user:2", "bob")
        cache.set("session:1", "data")

        keys = cache.keys()

        assert set(keys) == {"user:1", "user:2", "session:1"}

    def test_keys_with_pattern_filters(self) -> None:
        """Keys method with pattern returns matching keys only."""
        cache = InMemoryCache()
        cache.set("user:1", "alice")
        cache.set("user:2", "bob")
        cache.set("session:1", "data")

        user_keys = cache.keys("user:*")

        assert set(user_keys) == {"user:1", "user:2"}

    def test_keys_excludes_expired(self) -> None:
        """Keys method excludes expired keys."""
        cache = InMemoryCache()
        cache.set("persistent", "value")
        cache.set("temporary", "value", ttl=1)

        time.sleep(1.1)

        keys = cache.keys()

        assert "temporary" not in keys
        assert "persistent" in keys


class TestInMemoryCacheDataTypes:
    """Test InMemoryCache with different JSON value types."""

    def test_stores_strings(self) -> None:
        """Cache stores string values."""
        cache = InMemoryCache()
        cache.set("key", "hello world")

        assert cache.get("key") == "hello world"

    def test_stores_integers(self) -> None:
        """Cache stores integer values."""
        cache = InMemoryCache()
        cache.set("key", 42)

        assert cache.get("key") == 42

    def test_stores_floats(self) -> None:
        """Cache stores float values."""
        cache = InMemoryCache()
        cache.set("key", 3.14)

        assert cache.get("key") == 3.14

    def test_stores_booleans(self) -> None:
        """Cache stores boolean values."""
        cache = InMemoryCache()
        cache.set("key", True)

        assert cache.get("key") is True

    def test_stores_none(self) -> None:
        """Cache stores None values."""
        cache = InMemoryCache()
        cache.set("key", None)

        result = cache.get("key")
        assert result is None

    def test_stores_lists(self) -> None:
        """Cache stores list values."""
        cache = InMemoryCache()
        cache.set("key", [1, 2, 3])

        assert cache.get("key") == [1, 2, 3]

    def test_stores_dicts(self) -> None:
        """Cache stores dictionary values."""
        cache = InMemoryCache()
        cache.set("key", {"name": "Alice", "age": 30})

        assert cache.get("key") == {"name": "Alice", "age": 30}

    def test_stores_nested_structures(self) -> None:
        """Cache stores nested JSON structures."""
        cache = InMemoryCache()
        value = {
            "users": [
                {"name": "Alice", "scores": [95, 87, 92]},
                {"name": "Bob", "scores": [88, 91, 85]},
            ],
            "metadata": {"version": 1, "active": True},
        }
        cache.set("key", value)  # type: ignore

        assert cache.get("key") == value


class TestInMemoryCacheContextManager:
    """Test InMemoryCache context manager support."""

    def test_context_manager_entry(self) -> None:
        """Cache can be used as context manager."""
        with InMemoryCache() as cache:
            cache.set("key", "value")
            assert cache.get("key") == "value"

    def test_context_manager_exit(self) -> None:
        """Cache context manager exits cleanly."""
        cache = InMemoryCache()

        with cache:
            cache.set("key", "value")

        # Cache should still work after context exit
        assert cache.get("key") == "value"


class TestNoOpCacheBehavior:
    """Test NoOpCache input/output behavior."""

    def test_set_is_noop(self) -> None:
        """Setting a value in NoOpCache does nothing."""
        cache = NoOpCache()
        cache.set("key", "value")

        # No error should be raised
        assert True

    def test_get_always_returns_nothing(self) -> None:
        """Getting any key from NoOpCache returns None."""
        cache = NoOpCache()
        cache.set("key", "value")

        result = cache.get("key")

        assert result is None

    def test_delete_is_noop(self) -> None:
        """Deleting from NoOpCache does nothing."""
        cache = NoOpCache()

        # No error should be raised
        cache.delete("key")

    def test_clear_is_noop(self) -> None:
        """Clearing NoOpCache does nothing."""
        cache = NoOpCache()

        # No error should be raised
        cache.clear()

    def test_exists_always_returns_false(self) -> None:
        """Existence check in NoOpCache always returns False."""
        cache = NoOpCache()
        cache.set("key", "value")

        assert cache.exists("key") is False

    def test_context_manager(self) -> None:
        """NoOpCache can be used as context manager."""
        with NoOpCache() as cache:
            cache.set("key", "value")
            assert cache.get("key") is None


class TestCacheFactory:
    """Test cache factory function."""

    def test_create_in_memory_cache(self) -> None:
        """Factory creates InMemoryCache for 'in_memory' type."""
        result = create_cache("in_memory")

        assert result is not None
        assert isinstance(result, InMemoryCache)

    def test_create_in_memory_cache_with_ttl(self) -> None:
        """Factory creates InMemoryCache with default TTL."""
        result = create_cache("in_memory", default_ttl=60)

        assert result is not None
        assert isinstance(result, InMemoryCache)

    def test_create_noop_cache(self) -> None:
        """Factory creates NoOpCache for 'noop' type."""
        result = create_cache("noop")

        assert result is not None
        assert isinstance(result, NoOpCache)

    def test_create_unknown_type_returns_nothing(self) -> None:
        """Factory returns None for unknown cache type."""
        result = create_cache("unknown")

        assert result is None

    def test_create_redis_without_params_returns_nothing(self) -> None:
        """Factory returns None for redis without required params."""
        result = create_cache("redis")

        assert result is None

    def test_create_redis_partial_params_returns_nothing(self) -> None:
        """Factory returns None for redis with partial params."""
        result = create_cache("redis", host="localhost")

        assert result is None


class TestCacheTypeEnum:
    """Test CacheType enumeration."""

    def test_enum_values(self) -> None:
        """CacheType enum has expected values."""
        assert CacheType.REDIS.value == "redis"
        assert CacheType.IN_MEMORY.value == "in_memory"
        assert CacheType.NOOP.value == "noop"

    def test_enum_from_string(self) -> None:
        """CacheType can be created from string."""
        assert CacheType("redis") == CacheType.REDIS
        assert CacheType("in_memory") == CacheType.IN_MEMORY
        assert CacheType("noop") == CacheType.NOOP

    def test_invalid_enum_raises(self) -> None:
        """Invalid string raises ValueError."""
        with pytest.raises(ValueError):
            CacheType("invalid")
