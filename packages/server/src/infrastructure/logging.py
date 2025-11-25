"""Logging configuration for the InsightHub server."""

import logging
from typing import Dict, Any, Optional

from shared.logger import LogLevel, create_logger
from src.config import LOG_LEVEL, LOG_FORMAT


def configure_logging() -> None:
    """
    Configure application-wide logging.

    Sets up loggers for different components with appropriate levels and formats.
    """
    # Set root logger level to prevent duplicate messages
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)  # Only show warnings and above from libraries

    # Configure main application logger
    app_logger = create_logger("insighthub", LogLevel[LOG_LEVEL], LOG_FORMAT)
    app_logger.info("Logging configured", extra={
        "log_level": LOG_LEVEL,
        "log_format": LOG_FORMAT,
        "version": "1.0.0"
    })

    # Configure specific loggers for different components
    loggers_config = {
        "insighthub.api": LogLevel.INFO,
        "insighthub.auth": LogLevel.INFO,
        "insighthub.workspaces": LogLevel.INFO,
        "insighthub.chat": LogLevel.DEBUG,
        "insighthub.documents": LogLevel.INFO,
        "insighthub.middleware": LogLevel.INFO,
        "insighthub.infrastructure": LogLevel.INFO,
        "sqlalchemy": LogLevel.WARNING,  # Reduce SQLAlchemy noise
        "werkzeug": LogLevel.WARNING,    # Reduce Flask development server noise
    }

    for logger_name, level in loggers_config.items():
        logger = create_logger(logger_name, level, LOG_FORMAT)
        # Ensure the logger level is set correctly
        logger.setLevel(level.value)


def get_request_logger() -> logging.Logger:
    """Get a logger specifically for request handling."""
    return create_logger("insighthub.requests", LogLevel.INFO, LOG_FORMAT)


def get_security_logger() -> logging.Logger:
    """Get a logger specifically for security events."""
    return create_logger("insighthub.security", LogLevel.WARNING, LOG_FORMAT)


def get_performance_logger() -> logging.Logger:
    """Get a logger specifically for performance monitoring."""
    return create_logger("insighthub.performance", LogLevel.INFO, LOG_FORMAT)


def log_request_start(
    method: str,
    path: str,
    client_ip: str,
    user_id: Optional[int] = None,
    correlation_id: Optional[str] = None
) -> None:
    """Log the start of a request with structured data."""
    logger = get_request_logger()
    logger.info(
        f"Request started: {method} {path}",
        extra={
            "method": method,
            "path": path,
            "client_ip": client_ip,
            "user_id": user_id,
            "correlation_id": correlation_id,
            "event": "request_start"
        }
    )


def log_request_end(
    method: str,
    path: str,
    status_code: int,
    response_time_ms: float,
    correlation_id: Optional[str] = None
) -> None:
    """Log the end of a request with structured data."""
    logger = get_request_logger()
    level = logging.INFO if status_code < 400 else logging.WARNING if status_code < 500 else logging.ERROR

    logger.log(
        level,
        f"Request completed: {method} {path} - {status_code}",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "correlation_id": correlation_id,
            "event": "request_end"
        }
    )


def log_security_event(
    event: str,
    user_id: Optional[int] = None,
    client_ip: str = "",
    details: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> None:
    """Log a security-related event."""
    logger = get_security_logger()
    logger.warning(
        f"Security event: {event}",
        extra={
            "event": event,
            "user_id": user_id,
            "client_ip": client_ip,
            "correlation_id": correlation_id,
            "details": details or {},
            "security_event": True
        }
    )


def log_performance_metric(
    metric: str,
    value: float,
    tags: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> None:
    """Log a performance metric."""
    logger = get_performance_logger()
    logger.info(
        f"Performance metric: {metric} = {value}",
        extra={
            "metric": metric,
            "value": value,
            "correlation_id": correlation_id,
            "tags": tags or {},
            "performance_metric": True
        }
    )