"""Pagination value objects for consistent pagination across the application."""

from dataclasses import dataclass
from typing import Generic, List, TypeVar

from returns.result import Failure, Result, Success

T = TypeVar("T")


@dataclass(frozen=True)
class PaginationError:
    """Pagination validation error."""

    message: str
    field: str


@dataclass(frozen=True)
class Pagination:
    """Pagination parameters with validation.

    This value object encapsulates pagination parameters (skip, limit) with
    validation logic, eliminating duplicated validation across repository methods.
    Uses errors as values instead of exceptions.
    """

    skip: int
    limit: int
    max_limit: int = 100

    @staticmethod
    def create(
        skip: int = 0,
        limit: int = 50,
        max_limit: int = 100,
    ) -> Result["Pagination", PaginationError]:
        """Create pagination with validation - errors as values.

        Args:
            skip: Number of items to skip
            limit: Maximum items per page
            max_limit: Maximum allowed limit

        Returns:
            Result with Pagination or PaginationError
        """
        if skip < 0:
            return Failure(PaginationError(message="skip must be non-negative", field="skip"))

        if limit <= 0:
            return Failure(PaginationError(message="limit must be positive", field="limit"))

        if limit > max_limit:
            return Failure(
                PaginationError(message=f"limit must not exceed {max_limit}", field="limit")
            )

        return Success(Pagination(skip=skip, limit=limit, max_limit=max_limit))

    def is_cache_eligible(self) -> bool:
        """Check if results should be cached (first page, reasonable size)."""
        return self.skip == 0 and self.limit <= 50

    def offset_limit(self) -> tuple[int, int]:
        """Get SQL OFFSET and LIMIT values."""
        return self.skip, self.limit


@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    """Result of a paginated query.

    This value object replaces unclear Tuple[List[T], int] with self-documenting
    structure that makes pagination semantics explicit.
    """

    items: List[T]
    total_count: int
    skip: int = 0
    limit: int = 50

    @property
    def has_next_page(self) -> bool:
        """Check if there are more items beyond current page."""
        return (self.skip + self.limit) < self.total_count

    @property
    def has_previous_page(self) -> bool:
        """Check if there are items before current page."""
        return self.skip > 0

    @property
    def current_page_size(self) -> int:
        """Number of items in current page."""
        return len(self.items)

    @property
    def total_pages(self) -> int:
        """Total number of pages (given current limit)."""
        if self.limit == 0:
            return 0
        return (self.total_count + self.limit - 1) // self.limit
