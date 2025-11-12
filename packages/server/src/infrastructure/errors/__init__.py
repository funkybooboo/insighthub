"""Error handling infrastructure."""

from .base import DomainException, ValidationError
from .dtos import ErrorResponse
from .handlers import register_error_handlers

__all__ = ["DomainException", "ValidationError", "ErrorResponse", "register_error_handlers"]
