"""Exception types and DTOs for error handling."""

from .base import (
    AlreadyExistsError,
    ConflictError,
    DomainException,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from .dtos import ErrorResponse

__all__ = [
    "AlreadyExistsError",
    "ConflictError",
    "DomainException",
    "ErrorResponse",
    "ForbiddenError",
    "NotFoundError",
    "UnauthorizedError",
    "ValidationError",
]
