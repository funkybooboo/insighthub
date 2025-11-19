"""Logging configuration utilities for consistent logging across services."""

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(
    service_name: str,
    level: LogLevel = "INFO",
    format_string: str | None = None,
) -> logging.Logger:
    """
    Configure logging with consistent format across all services.
    
    Args:
        service_name: Name of the service (e.g., "ingestion-worker", "server")
        level: Logging level
        format_string: Custom format string (optional)
        
    Returns:
        Configured logger instance for the service
        
    Example:
        logger = setup_logging("ingestion-worker", "INFO")
        logger.info("Worker started")
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True,  # Override any existing configuration
    )
    
    # Get logger for this service
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level))
    
    # Suppress noisy third-party loggers
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module or component.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Processing document")
    """
    return logging.getLogger(name)
