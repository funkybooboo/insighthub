"""Generic mapper utilities (infrastructure).

These utilities are reusable across all domains. They use dependency injection
(composition) - pass in values and get formatted results back. No inheritance.
"""

from datetime import datetime


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO 8601 string.

    Args:
        dt: Datetime object to format

    Returns:
        ISO 8601 formatted string
    """
    return dt.isoformat()


def map_timestamps(created_at: datetime, updated_at: datetime) -> tuple[str, str]:
    """Map created_at and updated_at timestamps to ISO strings.

    Args:
        created_at: Creation timestamp
        updated_at: Update timestamp

    Returns:
        Tuple of (created_at_str, updated_at_str)
    """
    return (created_at.isoformat(), updated_at.isoformat())
