"""Structured logging configuration."""

import logging
import sys

from flask import Flask, has_request_context, request


class RequestContextFilter(logging.Filter):
    """
    Logging filter that adds request context to log records.

    Adds request ID, path, method, and user info to logs when available.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context to log record."""
        if has_request_context():
            record.request_id = getattr(request, "id", "no-request-id")
            record.path = request.path
            record.method = request.method
            record.remote_addr = request.remote_addr
        else:
            record.request_id = "no-request-id"
            record.path = "-"
            record.method = "-"
            record.remote_addr = "-"

        return True


class InfoFilter(logging.Filter):
    """Filter that only allows INFO and DEBUG messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Allow only INFO and DEBUG levels."""
        return record.levelno <= logging.INFO


def setup_logging(app: Flask, log_level: str = "INFO") -> None:
    """
    Set up structured logging for the application.

    Logs to stdout (INFO and below) and stderr (WARNING and above).
    This follows best practices for containerized applications where
    log aggregation systems collect from stdout/stderr.

    Configures:
    - stdout for INFO and DEBUG messages
    - stderr for WARNING, ERROR, and CRITICAL messages
    - Request context in all logs
    - Structured formatting

    Args:
        app: Flask application instance
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s] [%(request_id)s] "
        "[%(method)s %(path)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    formatter = detailed_formatter if app.debug else simple_formatter

    # stdout handler for INFO and DEBUG
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(RequestContextFilter())
    stdout_handler.addFilter(InfoFilter())

    # stderr handler for WARNING, ERROR, CRITICAL
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)
    stderr_handler.addFilter(RequestContextFilter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)

    # Log startup information
    app.logger.info(f"Logging configured (level: {log_level})")
    app.logger.info(f"Debug mode: {app.debug}")
    app.logger.info("Logging to stdout (INFO/DEBUG) and stderr (WARNING/ERROR/CRITICAL)")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
