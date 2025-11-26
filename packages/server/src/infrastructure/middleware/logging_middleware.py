"""Middleware for request/response logging."""

import time
from flask import Flask, g, request

from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def setup_logging_middleware(app: Flask) -> None:
    """
    Set up logging middleware.

    Logs all HTTP requests with timing information.

    Args:
        app: Flask application instance
    """
    @app.before_request
    def log_request_start() -> None:
        """Log request start and record start time."""
        g.start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
            },
        )

    @app.after_request
    def log_request_end(response):
        """Log request completion with duration."""
        if hasattr(g, "start_time"):
            duration_ms = (time.time() - g.start_time) * 1000
            logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code} ({duration_ms:.2f}ms)",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
        return response
