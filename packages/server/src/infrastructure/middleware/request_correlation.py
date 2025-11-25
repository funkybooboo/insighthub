"""Request correlation ID middleware for tracking requests across services."""

import uuid

from flask import Flask, Response, g, request


class RequestCorrelationMiddleware:
    """
    Middleware for generating and tracking request correlation IDs.

    Adds a unique correlation ID to each request for tracking across
    services, logging, and debugging.
    """

    def __init__(self, app: Flask, header_name: str = "X-Request-ID"):
        """
        Initialize correlation ID middleware.

        Args:
            app: Flask application instance
            header_name: HTTP header name for correlation ID
        """
        self.app = app
        self.header_name = header_name
        self.setup_correlation_tracking(app)

    def setup_correlation_tracking(self, app: Flask) -> None:
        """Set up request correlation tracking."""

        @app.before_request
        def generate_correlation_id() -> None:
            """Generate or extract correlation ID for the current request."""
            try:
                # Check if correlation ID is provided in request headers
                correlation_id = request.headers.get(self.header_name)

                # Generate new ID if not provided
                if not correlation_id:
                    correlation_id = str(uuid.uuid4())

                # Store in Flask g object for access throughout request
                g.correlation_id = correlation_id
            except Exception as e:
                # Don't break the request if correlation ID generation fails
                print(f"Warning: Failed to generate correlation ID: {e}")
                g.correlation_id = f"error-{str(uuid.uuid4())[:8]}"

        @app.after_request
        def add_correlation_header(response: Response) -> Response:
            """Add correlation ID to response headers."""
            try:
                correlation_id = getattr(g, "correlation_id", None)
                if correlation_id:
                    response.headers[self.header_name] = correlation_id
            except Exception as e:
                # Don't break the response if header addition fails
                print(f"Warning: Failed to add correlation header: {e}")
            return response

    @staticmethod
    def get_correlation_id() -> str | None:
        """Get the current request correlation ID."""
        return getattr(g, "correlation_id", None)
