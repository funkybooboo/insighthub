"""Request and response logging middleware."""

import logging
import time
from typing import Any

from flask import Flask, Request, Response, g, request

logger = logging.getLogger(__name__)


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
            g.start_time = time.time()

            # Get client IP (handle proxies)
            client_ip = self._get_client_ip(request)

            # Get user info if available
            user_info = "anonymous"
            if hasattr(g, "current_user") and g.current_user:
                user_info = f"user_id={g.current_user.id}"

            # Sanitize headers (remove sensitive data)
            headers = self._sanitize_headers(dict(request.headers))

            logger.info(
                f"Request started: {request.method} {request.path}",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "client_ip": client_ip,
                    "user_agent": request.user_agent.string,
                    "user": user_info,
                    "query_params": dict(request.args),
                    "headers": headers,
                },
            )

        @app.after_request
        def log_request_end(response: Response) -> Response:
            """Log the end of a request."""
            if hasattr(g, "start_time"):
                elapsed_time = time.time() - g.start_time
                logger.info(
                    f"Request completed: {request.method} {request.path} - {response.status_code}",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "status_code": response.status_code,
                        "response_time_ms": round(elapsed_time * 1000, 2),
                        "content_length": response.content_length,
                    },
                )

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

    def _sanitize_headers(self, headers: dict[str, Any]) -> dict[str, Any]:
        """
        Remove sensitive headers from logging.

        Removes Authorization tokens and other sensitive data.
        """
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        return {
            k: ("***REDACTED***" if k.lower() in sensitive_headers else v)
            for k, v in headers.items()
        }
