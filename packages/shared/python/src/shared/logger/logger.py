"""Logger wrapper providing a clean API for services and server."""

import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log levels for the logger wrapper."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """
    Logger wrapper providing structured logging for services and server.

    Provides a consistent logging interface across all InsightHub components
    with support for contextual information and structured output.

    Example:
        logger = Logger("ingestion-worker")
        logger.info("Processing document", document_id="doc_123")
        logger.error("Failed to process", error=str(e), document_id="doc_123")
    """

    _instances: dict[str, "Logger"] = {}
    _configured: bool = False

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
    ) -> None:
        """
        Initialize logger with name and level.

        Args:
            name: Logger name (typically service or module name)
            level: Minimum log level to output
        """
        self._name = name
        self._level = level
        self._logger = logging.getLogger(name)
        self._configure_logger()

    def _configure_logger(self) -> None:
        """Configure the underlying Python logger."""
        if not Logger._configured:
            format_string = (
                "%(asctime)s | %(name)s | %(levelname)s | "
                "[%(filename)s:%(lineno)d] | %(message)s"
            )
            logging.basicConfig(
                level=logging.DEBUG,
                format=format_string,
                handlers=[logging.StreamHandler(sys.stdout)],
                force=True,
            )
            # Suppress noisy third-party loggers
            logging.getLogger("pika").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("httpx").setLevel(logging.WARNING)
            Logger._configured = True

        self._logger.setLevel(getattr(logging, self._level.value))

    @classmethod
    def get_logger(cls, name: str, level: LogLevel = LogLevel.INFO) -> "Logger":
        """
        Get or create a logger instance.

        Uses singleton pattern per name to reuse logger instances.

        Args:
            name: Logger name
            level: Log level (only used when creating new instance)

        Returns:
            Logger instance
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name, level)
        return cls._instances[name]

    def _format_message(self, message: str, **context: Any) -> str:
        """Format message with context key-value pairs."""
        if not context:
            return message
        context_str = " | ".join(f"{k}={v}" for k, v in context.items())
        return f"{message} | {context_str}"

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with optional context."""
        self._logger.debug(self._format_message(message, **context))

    def info(self, message: str, **context: Any) -> None:
        """Log info message with optional context."""
        self._logger.info(self._format_message(message, **context))

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with optional context."""
        self._logger.warning(self._format_message(message, **context))

    def error(self, message: str, **context: Any) -> None:
        """Log error message with optional context."""
        self._logger.error(self._format_message(message, **context))

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message with optional context."""
        self._logger.critical(self._format_message(message, **context))

    def exception(self, message: str, **context: Any) -> None:
        """Log exception with traceback and optional context."""
        self._logger.exception(self._format_message(message, **context))

    def set_level(self, level: LogLevel) -> None:
        """Change the log level."""
        self._level = level
        self._logger.setLevel(getattr(logging, level.value))

    @property
    def name(self) -> str:
        """Get logger name."""
        return self._name

    @property
    def level(self) -> LogLevel:
        """Get current log level."""
        return self._level


def create_logger(name: str, level: LogLevel = LogLevel.INFO) -> Logger:
    """
    Create or get a logger instance.

    Factory function for creating loggers with a clean API.

    Args:
        name: Logger name (e.g., "server", "ingestion-worker")
        level: Minimum log level

    Returns:
        Logger instance

    Example:
        logger = create_logger("server", LogLevel.DEBUG)
        logger.info("Server started", port=8000)
    """
    return Logger.get_logger(name, level)
