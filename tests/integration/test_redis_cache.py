"""Integration tests for RedisCache with a real Redis instance."""

import pytest

from src.infrastructure.cache.redis_cache import RedisCache


@pytest.mark.integration
class TestRedisCacheIntegration:
    """Redis integration tests for the RedisCache component."""

    def test_cache_connection(self, cache_instance: RedisCache):
        """Test that the cache connection is established."""
        assert cache_instance._available is True
        assert cache_instance._client is not None
        assert cache_instance._client.ping() is True

    def test_set_and_get(self, cache_instance: RedisCache):
        """Test that we can set and get values from the cache."""
        # Arrange
        key, value = "test_key", "test_value"

        # Act
        cache_instance.set(key, value)
        retrieved_value = cache_instance.get(key)

        # Assert
        assert retrieved_value == value

    def test_get_nonexistent_key(self, cache_instance: RedisCache):
        """Test that getting a nonexistent key returns None."""
        # Act
        retrieved_value = cache_instance.get("nonexistent_key")

        # Assert
        assert retrieved_value is None

    def test_delete(self, cache_instance: RedisCache):
        """Test that we can delete a key from the cache."""
        # Arrange
        key, value = "key_to_delete", "value_to_delete"
        cache_instance.set(key, value)
        assert cache_instance.exists(key) is True

        # Act
        deleted = cache_instance.delete(key)

        # Assert
        assert deleted is True
        assert cache_instance.exists(key) is False
        assert cache_instance.get(key) is None

    def test_exists(self, cache_instance: RedisCache):
        """Test the 'exists' method."""
        # Arrange
        key, value = "existing_key", "existing_value"
        cache_instance.set(key, value)

        # Act & Assert
        assert cache_instance.exists(key) is True
        assert cache_instance.exists("nonexistent_key") is False

    def test_clear(self, cache_instance: RedisCache):
        """Test that we can clear the entire cache."""
        # Arrange
        cache_instance.set("key1", "value1")
        cache_instance.set("key2", "value2")
        assert cache_instance.exists("key1") is True
        assert cache_instance.exists("key2") is True

        # Act
        cache_instance.clear()

        # Assert
        assert cache_instance.exists("key1") is False
        assert cache_instance.exists("key2") is False
