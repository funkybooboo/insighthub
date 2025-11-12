"""Flask error handlers for centralized exception handling."""

from flask import Flask
from werkzeug.exceptions import HTTPException

from .base import DomainException
from .dtos import ErrorResponse


def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers with the Flask application.

    This enables centralized error handling where domain exceptions
    are automatically converted to appropriate HTTP responses.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(DomainException)
    def handle_domain_exception(error: DomainException) -> tuple[dict[str, str | int], int]:
        """
        Handle domain-specific exceptions.

        Args:
            error: Domain exception instance

        Returns:
            Tuple of (error dict, status code)
        """
        response = ErrorResponse.from_exception(error, error.status_code)
        return response.to_dict(), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> tuple[dict[str, str | int], int]:
        """
        Handle Werkzeug HTTP exceptions.

        Args:
            error: HTTP exception instance

        Returns:
            Tuple of (error dict, status code)
        """
        response = ErrorResponse.from_exception(error, error.code if error.code else 500)
        return response.to_dict(), error.code if error.code else 500

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception) -> tuple[dict[str, str | int], int]:
        """
        Handle unexpected exceptions.

        Args:
            error: Exception instance

        Returns:
            Tuple of (error dict, status code)
        """
        # Log the error for debugging
        app.logger.error(f"Unexpected error: {error}", exc_info=True)

        # Return generic error message to avoid leaking implementation details
        response = ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred. Please try again later.",
            status_code=500,
            timestamp=ErrorResponse.from_exception(error).timestamp,
        )
        return response.to_dict(), 500
