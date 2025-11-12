"""Data Transfer Objects for error responses."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ErrorResponse:
    """Standard error response format."""

    error: str
    message: str
    status_code: int
    timestamp: str

    @staticmethod
    def from_exception(exception: Exception, status_code: int = 500) -> "ErrorResponse":
        """
        Create ErrorResponse from an exception.

        Args:
            exception: The exception that occurred
            status_code: HTTP status code

        Returns:
            ErrorResponse DTO
        """
        return ErrorResponse(
            error=exception.__class__.__name__,
            message=str(exception),
            status_code=status_code,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

    def to_dict(self) -> dict[str, str | int]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation
        """
        return {
            "error": self.error,
            "message": self.message,
            "status_code": self.status_code,
            "timestamp": self.timestamp,
        }
