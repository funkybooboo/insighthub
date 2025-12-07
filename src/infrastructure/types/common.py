"""Common type aliases used across the application."""

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict, TypeVar

if TYPE_CHECKING:
    from returns.result import Result

E = TypeVar("E")
T = TypeVar("T")

# Metadata dictionary for storing arbitrary key-value pairs
MetadataDict = dict[str, str | int | float | bool | None]

# Filter dictionary for querying with conditions
FilterDict = dict[str, str | int | float | bool | None | list[str | int | float]]

# Primitive values
PrimitiveValue = str | int | float | bool | None


@dataclass(frozen=True)
class WorkspaceContext:
    """Value object encapsulating workspace identification and naming conventions.

    This eliminates magic strings for workspace collection names and cache keys
    by providing a single source of truth for workspace-related naming.
    """

    id: int

    @property
    def collection_name(self) -> str:
        """Vector/Graph collection name for this workspace.

        Returns:
            Collection name in format 'workspace_{id}'
        """
        return f"workspace_{self.id}"

    @property
    def cache_prefix(self) -> str:
        """Cache key prefix for this workspace.

        Returns:
            Cache prefix in format 'ws:{id}'
        """
        return f"ws:{self.id}"

    def cache_key(self, resource: str) -> str:
        """Generate cache key for workspace resource.

        Args:
            resource: Resource identifier (e.g., 'config', 'documents')

        Returns:
            Cache key in format 'ws:{id}:{resource}'
        """
        return f"{self.cache_prefix}:{resource}"


class ResultHandler:
    """Utilities for handling Result types in CLI commands.

    This class provides helper methods to unwrap Result types in CLI contexts,
    eliminating the repeated boilerplate of checking for Failure, extracting
    error messages, printing errors, and exiting.
    """

    @staticmethod
    def unwrap_or_exit(result: "Result[T, E]", operation: str) -> T:
        """Unwrap result or print error and exit.

        This method eliminates the common 4-line pattern:
            if isinstance(result, Failure):
                error = result.failure()
                message = getattr(error, 'message', str(error))
                IO.print_error(f"Error: {message}")
                sys.exit(1)
            value = result.unwrap()

        Args:
            result: Result to unwrap
            operation: Human-readable operation name for error message

        Returns:
            Unwrapped success value

        Exits:
            With code 1 if result is Failure
        """
        from returns.result import Failure

        if isinstance(result, Failure):
            error = result.failure()
            message = ResultHandler._format_error(error)
            # Use print to stderr to match CLI convention
            print(f"Error: {message}", file=sys.stderr)
            sys.exit(1)
        return result.unwrap()

    @staticmethod
    def _format_error(error: object) -> str:
        """Format error object into a user-friendly message.

        Handles common error types and extracts appropriate message.

        Args:
            error: Error object to format

        Returns:
            Formatted error message string
        """
        # Import here to avoid circular dependencies
        from src.infrastructure.types.errors import NotFoundError

        if isinstance(error, NotFoundError):
            return f"{error.resource} {error.id} not found"
        return getattr(error, "message", str(error))


# Health status for service health checks
class HealthStatus(TypedDict, total=False):
    """Health status dictionary for service health checks."""

    status: str
    provider: str
    model_available: bool
