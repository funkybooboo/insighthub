"""Common type aliases used across the application."""

from typing import Optional, TypedDict

# Metadata dictionary for storing arbitrary key-value pairs
MetadataDict = dict[str, str | int | float | bool | None]

# Filter dictionary for querying with conditions
FilterDict = dict[str, str | int | float | bool | None | list[str | int | float]]

# Primitive values
PrimitiveValue = str | int | float | bool | None


# Health status for service health checks
class HealthStatus(TypedDict, total=False):
    """Health status dictionary for service health checks."""

    status: str
    provider: str
    model_available: bool
