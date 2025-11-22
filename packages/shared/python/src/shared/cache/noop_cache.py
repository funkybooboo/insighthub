"""No-operation cache implementation."""

from __future__ import annotations

from types import TracebackType

from shared.types.common import JsonValue
from shared.types.option import Nothing, Option

from .cache import Cache


class NoOpCache(Cache):
    """
    No-operation cache that does nothing.

    Useful for testing or when caching is disabled.
    All operations are no-ops and get() always returns Nothing().

    Example:
        cache = NoOpCache()
        cache.set("key", "value")  # Does nothing
        result = cache.get("key")  # Always returns Nothing()
    """

    def set(self, key: str, value: JsonValue, ttl: int | None = None) -> None:
        """No-op set operation."""
        pass

    def get(self, key: str) -> Option[JsonValue]:
        """Always returns Nothing()."""
        return Nothing()

    def delete(self, key: str) -> None:
        """No-op delete operation."""
        pass

    def clear(self) -> None:
        """No-op clear operation."""
        pass

    def exists(self, key: str) -> bool:
        """Always returns False."""
        return False

    def __enter__(self) -> "NoOpCache":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        pass
