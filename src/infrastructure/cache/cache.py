from typing import Any, Optional


class Cache:
    """Abstract cache interface."""

    def get(self, key: str) -> Any:
        """Get value from cache."""
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all cache entries."""
        raise NotImplementedError
