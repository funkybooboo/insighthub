"""Exception types and DTOs for error handling."""

from .base import DomainException
from .dtos import ErrorResponse

__all__ = ["DomainException", "ErrorResponse"]
