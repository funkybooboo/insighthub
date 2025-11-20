"""Result type for error handling without exceptions."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Success result containing a value."""

    value: T

    def is_ok(self) -> bool:
        """Check if result is Ok."""
        return True

    def is_err(self) -> bool:
        """Check if result is Err."""
        return False

    def unwrap(self) -> T:
        """Get the success value."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get the success value or default."""
        return self.value

    def map(self, func):
        """Map the success value to a new value."""
        return Ok(func(self.value))


@dataclass(frozen=True)
class Err(Generic[E]):
    """Error result containing an error."""

    error: E

    def is_ok(self) -> bool:
        """Check if result is Ok."""
        return False

    def is_err(self) -> bool:
        """Check if result is Err."""
        return True

    def unwrap(self):
        """Raise exception when trying to unwrap error."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default):
        """Get the default value since this is an error."""
        return default

    def map(self, func):
        """Return self since this is an error."""
        return self


# Type alias for Result
Result = Ok[T] | Err[E]
