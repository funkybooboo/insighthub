"""Error handling middleware."""

from flask import Flask, Response, jsonify

from src.infrastructure.exceptions import (
    AlreadyExistsError,
    ApplicationError,
    NotFoundError,
    ValidationError,
)
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def setup_error_handlers(app: Flask) -> None:
    """
    Set up error handlers for common exceptions.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(NotFoundError)
    def handle_not_found(error: NotFoundError) -> tuple[Response, int]:
        """Handle resource not found errors."""
        logger.warning(f"Not found: {error.message}")
        return jsonify({"error": error.message, "code": error.code}), 404

    @app.errorhandler(AlreadyExistsError)
    def handle_already_exists(error: AlreadyExistsError) -> tuple[Response, int]:
        """Handle resource already exists errors."""
        logger.warning(f"Already exists: {error.message}")
        return jsonify({"error": error.message, "code": error.code}), 409

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> tuple[Response, int]:
        """Handle validation errors."""
        logger.warning(f"Validation error: {error.message}")
        return jsonify({"error": error.message, "code": error.code}), 400

    @app.errorhandler(ApplicationError)
    def handle_application_error(error: ApplicationError) -> tuple[Response, int]:
        """Handle general application errors."""
        logger.error(f"Application error: {error.message}")
        return jsonify({"error": error.message, "code": error.code}), 500

    @app.errorhandler(404)
    def handle_404(error) -> tuple[Response, int]:
        """Handle 404 errors."""
        return jsonify({"error": "Not found", "code": "NOT_FOUND"}), 404

    @app.errorhandler(500)
    def handle_500(error) -> tuple[Response, int]:
        """Handle 500 errors."""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> tuple[Response, int]:
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {str(error)}", exc_info=error)
        return jsonify({"error": "Internal server error", "code": "INTERNAL_ERROR"}), 500
