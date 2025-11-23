"""
Integration tests for cache module.

These tests verify that cache implementations work correctly together
with the factory and other components.
"""

import pytest

from shared.cache.cache import Cache
from shared.cache.factory import create_cache
from shared.cache.in_memory_cache import InMemoryCache
from shared.cache.noop_cache import NoOpCache


class TestCacheFactoryIntegration:
    """Integration tests for cache factory with implementations."""

    def test_in_memory_cache_full_workflow(self) -> None:
        """Test complete workflow with InMemoryCache from factory."""
        result = create_cache("in_memory", default_ttl=300)
        assert result.is_some()

        cache = result.unwrap()

        # Set values
        cache.set("user:1", {"name": "Alice", "active": True})
        cache.set("user:2", {"name": "Bob", "active": False})
        cache.set("counter", 42)

        # Get values
        user1 = cache.get("user:1")
        assert user1.is_some()
        assert user1.unwrap() == {"name": "Alice", "active": True}

        counter = cache.get("counter")
        assert counter.is_some()
        assert counter.unwrap() == 42

        # Check existence
        assert cache.exists("user:1") is True
        assert cache.exists("user:999") is False

        # Delete
        cache.delete("user:2")
        assert cache.exists("user:2") is False

        # Clear
        cache.clear()
        assert cache.get("user:1").is_nothing()
        assert cache.get("counter").is_nothing()

    def test_noop_cache_full_workflow(self) -> None:
        """Test complete workflow with NoOpCache from factory."""
        result = create_cache("noop")
        assert result.is_some()

        cache = result.unwrap()

        # All operations should be no-ops
        cache.set("key", "value")
        assert cache.get("key").is_nothing()
        assert cache.exists("key") is False

        cache.delete("key")  # Should not raise
        cache.clear()  # Should not raise

    def test_factory_returns_correct_implementation_types(self) -> None:
        """Factory returns correct implementation types."""
        in_memory_result = create_cache("in_memory")
        noop_result = create_cache("noop")

        assert isinstance(in_memory_result.unwrap(), InMemoryCache)
        assert isinstance(noop_result.unwrap(), NoOpCache)

    def test_factory_with_invalid_type(self) -> None:
        """Factory handles invalid cache type."""
        result = create_cache("invalid_type")

        assert result.is_nothing()


class TestCacheContextManagerIntegration:
    """Integration tests for cache context manager usage."""

    def test_in_memory_cache_context_manager(self) -> None:
        """InMemoryCache works correctly as context manager."""
        result = create_cache("in_memory")
        cache = result.unwrap()

        with cache:
            cache.set("key", "value")
            assert cache.get("key").unwrap() == "value"

        # Cache should still work after context
        assert cache.get("key").unwrap() == "value"

    def test_noop_cache_context_manager(self) -> None:
        """NoOpCache works correctly as context manager."""
        result = create_cache("noop")
        cache = result.unwrap()

        with cache:
            cache.set("key", "value")
            assert cache.get("key").is_nothing()


class TestCachePolymorphism:
    """Integration tests for cache polymorphic behavior."""

    def test_caches_share_common_interface(self) -> None:
        """All cache implementations share common interface."""
        caches: list[Cache] = [
            create_cache("in_memory").unwrap(),
            create_cache("noop").unwrap(),
        ]

        for cache in caches:
            # All should have the same methods
            cache.set("test_key", "test_value")
            cache.get("test_key")
            cache.exists("test_key")
            cache.delete("test_key")
            cache.clear()

    def test_swap_cache_implementation(self) -> None:
        """Can swap cache implementation without changing usage code."""

        def use_cache(cache: Cache, key: str, value: str) -> bool:
            cache.set(key, value)
            return cache.exists(key)

        in_memory = create_cache("in_memory").unwrap()
        noop = create_cache("noop").unwrap()

        # Same function works with both implementations
        assert use_cache(in_memory, "key", "value") is True
        assert use_cache(noop, "key", "value") is False


class TestCacheWithComplexData:
    """Integration tests for cache with complex data structures."""

    def test_cache_nested_json_structure(self) -> None:
        """Cache correctly stores and retrieves nested JSON."""
        cache = create_cache("in_memory").unwrap()

        complex_data = {
            "user": {
                "id": 123,
                "profile": {
                    "name": "Alice",
                    "tags": ["developer", "python", "ai"],
                    "settings": {
                        "theme": "dark",
                        "notifications": True,
                        "limits": {"daily": 100, "monthly": 1000},
                    },
                },
            },
            "metadata": {"version": 1.5, "active": True, "extras": None},
        }

        cache.set("complex", complex_data)
        retrieved = cache.get("complex")

        assert retrieved.is_some()
        assert retrieved.unwrap() == complex_data

    def test_cache_list_of_objects(self) -> None:
        """Cache correctly stores and retrieves list of objects."""
        cache = create_cache("in_memory").unwrap()

        items = [
            {"id": 1, "name": "Item 1", "active": True},
            {"id": 2, "name": "Item 2", "active": False},
            {"id": 3, "name": "Item 3", "active": True},
        ]

        cache.set("items", items)
        retrieved = cache.get("items")

        assert retrieved.is_some()
        assert retrieved.unwrap() == items
        assert len(retrieved.unwrap()) == 3
