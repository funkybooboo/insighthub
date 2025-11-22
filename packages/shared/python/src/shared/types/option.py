"""
Option type for null-safe operations.

Option represents a value that may or may not exist, eliminating None checks.
Use Option instead of returning None to make intent explicit.

Examples:
    # Bad: ambiguous None
    def find_user(id: int) -> User | None:
        return None  # Not found? Error? Unknown!
    
    # Good: explicit Option
    def find_user(id: int) -> Option[User]:
        return Nothing()  # Clearly indicates "no value"
"""

from dataclasses import dataclass
from typing import Callable, Generic, NoReturn, TypeVar

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Some(Generic[T]):
    """Represents a value that exists."""

    value: T

    def is_some(self) -> bool:
        """Check if this is Some."""
        return True

    def is_nothing(self) -> bool:
        """Check if this is Nothing."""
        return False

    def unwrap(self) -> T:
        """Get the value."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get the value or default (returns value)."""
        return self.value

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        """Get the value or compute default (returns value)."""
        return self.value

    def map(self, f: Callable[[T], U]) -> "Option[U]":
        """Transform the value if it exists."""
        return Some(f(self.value))

    def and_then(self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        """Chain operations that return Option."""
        return f(self.value)

    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        """Filter the value based on predicate."""
        if predicate(self.value):
            return self
        return Nothing()

    def or_else(self, f: Callable[[], "Option[T]"]) -> "Option[T]":
        """Return this Option (ignores alternative)."""
        return self


@dataclass(frozen=True)
class Nothing:
    """Represents the absence of a value."""

    def is_some(self) -> bool:
        """Check if this is Some."""
        return False

    def is_nothing(self) -> bool:
        """Check if this is Nothing."""
        return True

    def unwrap(self) -> NoReturn:
        """Raise exception when trying to unwrap Nothing."""
        raise ValueError("Called unwrap on Nothing")

    def unwrap_or(self, default: T) -> T:
        """Get the default value since this is Nothing."""
        return default

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        """Compute and return default value."""
        return f()

    def map(self, f: Callable[[T], U]) -> "Nothing":
        """Return Nothing (no value to transform)."""
        return self

    def and_then(self, f: Callable[[T], "Option[U]"]) -> "Nothing":
        """Return Nothing (no value to chain)."""
        return self

    def filter(self, predicate: Callable[[T], bool]) -> "Nothing":
        """Return Nothing (no value to filter)."""
        return self

    def or_else(self, f: Callable[[], "Option[T]"]) -> "Option[T]":
        """Compute and return alternative Option."""
        return f()


# Type alias for Option
Option = Some[T] | Nothing


def from_nullable(value: T | None) -> Option[T]:
    """
    Convert a nullable value to Option.

    Examples:
        >>> from_nullable(42)
        Some(42)
        >>> from_nullable(None)
        Nothing()
    """
    if value is None:
        return Nothing()
    return Some(value)


def from_result(result: "Some[T] | Nothing", error_value: U | None = None) -> Option[T]:
    """
    Convert a Result to Option, discarding error information.

    Use when you don't care about the specific error, just whether
    the operation succeeded.
    """
    if hasattr(result, "is_ok") and result.is_ok():
        return Some(result.unwrap())
    return Nothing()
