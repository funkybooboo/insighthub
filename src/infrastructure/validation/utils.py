"""Generic validation utilities (infrastructure).

These validators are reusable across all domains. They use dependency injection
(composition) - pass in values and get Results back. No inheritance.
"""

from typing import Optional

from returns.result import Failure, Result, Success

from src.infrastructure.types import ValidationError


def validate_positive_id(value: int, field_name: str) -> Result[int, ValidationError]:
    """Validate that an ID is positive.

    Args:
        value: ID value to validate
        field_name: Name of the field (for error messages)

    Returns:
        Result with validated ID or ValidationError
    """
    if value <= 0:
        return Failure(ValidationError(f"{field_name} must be positive", field=field_name))
    return Success(value)


def validate_pagination(
    skip: int, limit: int, max_limit: int = 100
) -> Result[tuple[int, int], ValidationError]:
    """Validate pagination parameters.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        max_limit: Maximum allowed limit value

    Returns:
        Result with validated (skip, limit) tuple or ValidationError
    """
    if skip < 0:
        return Failure(ValidationError("Skip must be non-negative", field="skip"))

    if limit <= 0:
        return Failure(ValidationError("Limit must be positive", field="limit"))

    if limit > max_limit:
        return Failure(ValidationError(f"Limit cannot exceed {max_limit}", field="limit"))

    return Success((skip, limit))


def validate_non_empty_string(
    value: Optional[str],
    field_name: str,
    max_length: Optional[int] = None,
    required: bool = True,
) -> Result[str, ValidationError]:
    """Validate that a string is non-empty and optionally check max length.

    Args:
        value: String value to validate
        field_name: Name of the field (for error messages)
        max_length: Optional maximum length
        required: Whether the field is required

    Returns:
        Result with validated string or ValidationError
    """
    if value is None or value.strip() == "":
        if required:
            return Failure(ValidationError(f"{field_name} cannot be empty", field=field_name))
        return Success("")

    cleaned = value.strip()

    if max_length is not None and len(cleaned) > max_length:
        return Failure(
            ValidationError(
                f"{field_name} cannot exceed {max_length} characters",
                field=field_name,
            )
        )

    return Success(cleaned)
