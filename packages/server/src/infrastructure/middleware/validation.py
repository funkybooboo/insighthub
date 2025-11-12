"""Request validation middleware."""

import logging
from typing import Any

from flask import Flask, Request, jsonify, request

logger = logging.getLogger(__name__)


class RequestValidationMiddleware:
    """
    Middleware for validating incoming requests.

    Performs security checks:
    - Content-Type validation
    - Request size limits
    - Content validation for JSON endpoints
    - Path traversal prevention
    """

    def __init__(
        self,
        app: Flask,
        max_content_length: int = 16 * 1024 * 1024,  # 16MB default
        allowed_content_types: list[str] | None = None,
    ) -> None:
        """
        Initialize request validation middleware.

        Args:
            app: Flask application instance
            max_content_length: Maximum allowed request size in bytes
            allowed_content_types: List of allowed content types
        """
        self.app = app
        self.max_content_length = max_content_length
        self.allowed_content_types = allowed_content_types or [
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
            "text/plain",
        ]
        self.setup_validation(app)
        logger.info("Request validation middleware initialized")

    def setup_validation(self, app: Flask) -> None:
        """Set up request validation before each request."""

        @app.before_request
        def validate_request() -> Any:
            """Validate the incoming request."""
            # Skip validation for health checks and OPTIONS requests
            if request.method == "OPTIONS" or request.path in ["/health", "/heartbeat"]:
                return None

            # Validate content length
            if request.content_length and request.content_length > self.max_content_length:
                logger.warning(
                    f"Request too large: {request.content_length} bytes "
                    f"(max: {self.max_content_length})"
                )
                return (
                    jsonify(
                        {
                            "error": "Request entity too large",
                            "max_size_bytes": self.max_content_length,
                        }
                    ),
                    413,
                )

            # Validate Content-Type for POST/PUT/PATCH requests
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.content_type or ""

                # Extract base content type (ignore charset, boundary, etc.)
                base_content_type = content_type.split(";")[0].strip()

                if base_content_type and not any(
                    allowed in content_type.lower() for allowed in self.allowed_content_types
                ):
                    logger.warning(f"Invalid Content-Type: {content_type}")
                    return (
                        jsonify(
                            {
                                "error": "Unsupported Content-Type",
                                "allowed_types": self.allowed_content_types,
                            }
                        ),
                        415,
                    )

            # Validate JSON content for application/json requests
            if (
                request.is_json
                and request.method in ["POST", "PUT", "PATCH"]
                and request.content_length
                and request.content_length > 0
            ):
                try:
                    request.get_json(force=True)
                except Exception as e:
                    logger.warning(f"Invalid JSON payload: {str(e)}")
                    return jsonify({"error": "Invalid JSON payload"}), 400

            # Prevent path traversal attacks
            if self._contains_path_traversal(request.path):
                logger.warning(f"Path traversal attempt detected: {request.path}")
                return jsonify({"error": "Invalid request path"}), 400

            return None

    def _contains_path_traversal(self, path: str) -> bool:
        """
        Check if the path contains path traversal patterns.

        Looks for patterns like ../, ..\, etc.
        """
        dangerous_patterns = ["../", "..\\", "%2e%2e", "%252e"]
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in dangerous_patterns)
