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
        cache = create_cache("in_memory", default_ttl=300)
        assert cache is not None

        # Set values
        cache.set("user:1", {"name": "Alice", "active": True})
        cache.set("user:2", {"name": "Bob", "active": False})
        cache.set("counter", 42)

        # Get values
        user1 = cache.get("user:1")
        assert user1 is not None
        assert user1 == {"name": "Alice", "active": True}

        counter = cache.get("counter")
        assert counter is not None
        assert counter == 42

        # Check existence
        assert cache.exists("user:1") is True
        assert cache.exists("user:999") is False

        # Delete
        cache.delete("user:2")
        assert cache.exists("user:2") is False

        # Clear
        cache.clear()
        assert cache.get("user:1") is None
        assert cache.get("counter") is None

    def test_noop_cache_full_workflow(self) -> None:
        """Test complete workflow with NoOpCache from factory."""
        cache = create_cache("noop")
        assert cache is not None

        # All operations should be no-ops
        cache.set("key", "value")
        assert cache.get("key") is None
        assert cache.exists("key") is False

        cache.delete("key")  # Should not raise
        cache.clear()  # Should not raise

    def test_factory_returns_correct_implementation_types(self) -> None:
        """Factory returns correct implementation types."""
        in_memory_result = create_cache("in_memory")
        noop_result = create_cache("noop")

        assert isinstance(in_memory_result, InMemoryCache)
        assert isinstance(noop_result, NoOpCache)

    def test_factory_with_invalid_type(self) -> None:
        """Factory handles invalid cache type."""
        result = create_cache("invalid_type")

        assert result is None


class TestCacheContextManagerIntegration:
    """Integration tests for cache context manager usage."""

    def test_in_memory_cache_context_manager(self) -> None:
        """InMemoryCache works correctly as context manager."""
        cache = create_cache("in_memory")
        assert cache is not None

        with cache:
            cache.set("key", "value")
            assert cache.get("key") == "value"

        # Cache should still work after context
        assert cache.get("key") == "value"

    def test_noop_cache_context_manager(self) -> None:
        """NoOpCache works correctly as context manager."""
        cache = create_cache("noop")
        assert cache is not None

        with cache:
            cache.set("key", "value")
            assert cache.get("key") is None


class TestCachePolymorphism:
    """Integration tests for cache polymorphic behavior."""

    def test_caches_share_common_interface(self) -> None:
        """All cache implementations share common interface."""
        in_memory_cache = create_cache("in_memory")
        noop_cache = create_cache("noop")
        assert in_memory_cache is not None
        assert noop_cache is not None
        caches: list[Cache] = [
            in_memory_cache,
            noop_cache,
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

        in_memory = create_cache("in_memory")
        noop = create_cache("noop")
        assert in_memory is not None
        assert noop is not None

        # Same function works with both implementations
        assert use_cache(in_memory, "key", "value") is True
        assert use_cache(noop, "key", "value") is False


class TestCacheWithComplexData:
    """Integration tests for cache with complex data structures."""

    def test_cache_nested_json_structure(self) -> None:
        """Cache correctly stores and retrieves nested JSON."""
        cache = create_cache("in_memory")
        assert cache is not None

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

        assert retrieved is not None
        assert retrieved == complex_data

    def test_cache_list_of_objects(self) -> None:
        """Cache correctly stores and retrieves list of objects."""
        cache = create_cache("in_memory")
        assert cache is not None

        items = [
            {"id": 1, "name": "Item 1", "active": True},
            {"id": 2, "name": "Item 2", "active": False},
            {"id": 3, "name": "Item 3", "active": True},
        ]

        cache.set("items", items)
        retrieved = cache.get("items")

        assert retrieved is not None
        assert retrieved == items
        assert len(retrieved) == 3
