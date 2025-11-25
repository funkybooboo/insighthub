"""Request and response logging middleware."""

import time

from flask import Flask, Request, Response, g, request
from shared.logger import create_logger

logger = create_logger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware for logging all incoming requests and outgoing responses.

    Logs:
    - Request method, path, IP address
    - Request headers (sanitized)
    - Response status code
    - Response time
    - User ID (if authenticated)
    """

    def __init__(self, app: Flask) -> None:
        """Initialize the logging middleware."""
        self.app = app
        self.setup_logging(app)

    def setup_logging(self, app: Flask) -> None:
        """Set up request and response logging hooks."""

        @app.before_request
        def log_request_start() -> None:
            """Log the start of a request."""
            try:
                g.start_time = time.time()

                # Get client IP (handle proxies)
                client_ip = self._get_client_ip(request)

                # Get user info if available
                user_id = None
                if hasattr(g, "current_user") and g.current_user:
                    user_id = g.current_user.id

                # Get correlation ID if available
                correlation_id = getattr(g, 'correlation_id', None)

                # Log request start using structured logging
                from src.infrastructure.logging import log_request_start
                log_request_start(
                    method=request.method,
                    path=request.path,
                    client_ip=client_ip,
                    user_id=user_id,
                    correlation_id=correlation_id
                )

            except Exception as e:
                # Don't break the request if logging fails
                print(f"Warning: Request logging failed: {e}")

        @app.after_request
        def log_request_end(response: Response) -> Response:
            """Log the end of a request."""
            try:
                if hasattr(g, "start_time"):
                    elapsed_time = time.time() - g.start_time
                    # Get correlation ID if available
                    correlation_id = getattr(g, 'correlation_id', None)

                    # Log request end using structured logging
                    from src.infrastructure.logging import log_request_end
                    log_request_end(
                        method=request.method,
                        path=request.path,
                        status_code=response.status_code,
                        response_time_ms=round(elapsed_time * 1000, 2),
                        correlation_id=correlation_id
                    )
            except Exception as e:
                # Don't break the response if logging fails
                print(f"Warning: Response logging failed: {e}")
            return response

    def _get_client_ip(self, req: Request) -> str:
        """
        Get the real client IP address, handling proxies.

        Checks X-Forwarded-For and X-Real-IP headers first.
        """
        if req.headers.get("X-Forwarded-For"):
            return req.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if req.headers.get("X-Real-IP"):
            return req.headers.get("X-Real-IP", "")
        return req.remote_addr or "unknown"

    def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """
        Remove sensitive headers from logging.

        Removes Authorization tokens and other sensitive data.
        """
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        return {
            k: ("***REDACTED***" if k.lower() in sensitive_headers else v)
            for k, v in headers.items()
        }
