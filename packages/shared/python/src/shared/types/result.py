"""Result type for error handling without exceptions."""

from dataclasses import dataclass
from typing import Callable, Generic, NoReturn, TypeVar

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


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

    def map(self, func: Callable[[T], U]) -> "Ok[U]":
        """Map the success value to a new value."""
        return Ok(func(self.value))

    def map_err(self, func: Callable[[E], U]) -> "Ok[T]":
        """Return self since this is not an error."""
        return self

    def ok(self) -> T:
        """Get the success value (alias for unwrap)."""
        return self.value

    def err(self) -> NoReturn:
        """This is not an error, so this should not be called."""
        raise ValueError("Called err() on Ok")


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

    def unwrap(self) -> NoReturn:
        """Raise exception when trying to unwrap error."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Get the default value since this is an error."""
        return default

    def map(self, func: Callable[[T], U]) -> "Err[E]":
        """Return self since this is an error."""
        return self

    def map_err(self, func: Callable[[E], U]) -> "Err[U]":
        """Map the error to a new error."""
        return Err(func(self.error))

    def ok(self) -> NoReturn:
        """This is an error, so this should not be called."""
        raise ValueError("Called ok() on Err")

    def err(self) -> E:
        """Get the error value."""
        return self.error


# Type alias for Result (note: this is a union type for documentation purposes)
# In practice, use Ok[T] | Err[E] directly for proper type inference
Result = Ok[T] | Err[E]
