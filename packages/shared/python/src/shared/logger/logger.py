"""Logger wrapper providing a clean API for services and server."""

import logging
import re
import sys
from enum import Enum

# Type alias for context values - primitives only, no Any
ContextValue = str | int | float | bool | None


class LogLevel(Enum):
    """Log levels for the logger wrapper."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SecretsFilter(logging.Filter):
    """
    Logging filter that redacts sensitive information from log messages.

    Patterns detected and redacted:
    - API keys and tokens
    - Passwords
    - Bearer tokens
    - AWS credentials
    - Connection strings with credentials
    - JWT tokens
    """

    # Patterns for sensitive data
    SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        # API keys (common formats)
        (
            re.compile(r'api[_-]?key["\s:=]+["\']?[\w\-]{20,}["\']?', re.IGNORECASE),
            'api_key="[REDACTED]"',
        ),
        (
            re.compile(r'apikey["\s:=]+["\']?[\w\-]{20,}["\']?', re.IGNORECASE),
            'apikey="[REDACTED]"',
        ),
        # Bearer tokens
        (re.compile(r"Bearer\s+[\w\-_.]+", re.IGNORECASE), "Bearer [REDACTED]"),
        # Authorization headers
        (
            re.compile(r'Authorization["\s:=]+["\']?[\w\-_.]+["\']?', re.IGNORECASE),
            'Authorization="[REDACTED]"',
        ),
        # Passwords
        (
            re.compile(r'password["\s:=]+["\']?[^\s"\']+["\']?', re.IGNORECASE),
            'password="[REDACTED]"',
        ),
        (re.compile(r'passwd["\s:=]+["\']?[^\s"\']+["\']?', re.IGNORECASE), 'passwd="[REDACTED]"'),
        (re.compile(r'pwd["\s:=]+["\']?[^\s"\']+["\']?', re.IGNORECASE), 'pwd="[REDACTED]"'),
        # Secret keys
        (
            re.compile(r'secret[_-]?key["\s:=]+["\']?[\w\-]{16,}["\']?', re.IGNORECASE),
            'secret_key="[REDACTED]"',
        ),
        (
            re.compile(r'secret["\s:=]+["\']?[\w\-]{16,}["\']?', re.IGNORECASE),
            'secret="[REDACTED]"',
        ),
        # AWS credentials
        (
            re.compile(
                r'aws[_-]?access[_-]?key[_-]?id["\s:=]+["\']?[\w]{16,}["\']?', re.IGNORECASE
            ),
            'aws_access_key_id="[REDACTED]"',
        ),
        (
            re.compile(
                r'aws[_-]?secret[_-]?access[_-]?key["\s:=]+["\']?[\w/+=]{16,}["\']?', re.IGNORECASE
            ),
            'aws_secret_access_key="[REDACTED]"',
        ),
        # JWT tokens (three base64 parts separated by dots)
        (re.compile(r"eyJ[\w\-_]+\.eyJ[\w\-_]+\.[\w\-_]+"), "[JWT_REDACTED]"),
        # Connection strings with credentials
        (re.compile(r"://[^:]+:[^@]+@", re.IGNORECASE), "://[CREDENTIALS_REDACTED]@"),
        # Private keys
        (
            re.compile(
                r"-----BEGIN\s+[\w\s]+PRIVATE\s+KEY-----[\s\S]*?-----END\s+[\w\s]+PRIVATE\s+KEY-----"
            ),
            "[PRIVATE_KEY_REDACTED]",
        ),
        # Token patterns
        (
            re.compile(r'token["\s:=]+["\']?[\w\-_.]{20,}["\']?', re.IGNORECASE),
            'token="[REDACTED]"',
        ),
        # Access tokens
        (
            re.compile(r'access[_-]?token["\s:=]+["\']?[\w\-_.]{20,}["\']?', re.IGNORECASE),
            'access_token="[REDACTED]"',
        ),
        # Refresh tokens
        (
            re.compile(r'refresh[_-]?token["\s:=]+["\']?[\w\-_.]{20,}["\']?', re.IGNORECASE),
            'refresh_token="[REDACTED]"',
        ),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record, redacting any sensitive information.

        Args:
            record: Log record to filter

        Returns:
            Always True (we filter content, not records)
        """
        if record.msg:
            record.msg = self._redact_secrets(str(record.msg))
        if record.args:
            record.args = tuple(
                self._redact_secrets(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True

    def _redact_secrets(self, text: str) -> str:
        """
        Redact sensitive information from text.

        Args:
            text: Text to redact

        Returns:
            Text with secrets redacted
        """
        for pattern, replacement in self.SECRET_PATTERNS:
            text = pattern.sub(replacement, text)
        return text


class Logger:
    """
    Logger wrapper providing structured logging for services and server.

    Provides a consistent logging interface across all InsightHub components
    with support for contextual information, structured output, and automatic
    secrets filtering.

    Example:
        logger = Logger("ingestion-worker")
        logger.info("Processing document", document_id="doc_123")
        logger.error("Failed to process", error=str(e), document_id="doc_123")
    """

    _instances: dict[str, "Logger"] = {}
    _configured: bool = False
    _secrets_filter: SecretsFilter = SecretsFilter()

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
        """Configure the underlying Python logger with secrets filtering."""
        if not Logger._configured:
            format_string = (
                "%(asctime)s | %(name)s | %(levelname)s | "
                "[%(filename)s:%(lineno)d] | %(message)s"
            )

            # Create handler with secrets filter
            handler = logging.StreamHandler(sys.stdout)
            handler.addFilter(Logger._secrets_filter)

            logging.basicConfig(
                level=logging.DEBUG,
                format=format_string,
                handlers=[handler],
                force=True,
            )

            # Add secrets filter to root logger as well
            logging.getLogger().addFilter(Logger._secrets_filter)

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

    def _format_message(self, message: str, **context: ContextValue) -> str:
        """Format message with context key-value pairs."""
        if not context:
            return message
        context_str = " | ".join(f"{k}={v}" for k, v in context.items())
        return f"{message} | {context_str}"

    def debug(self, message: str, **context: ContextValue) -> None:
        """Log debug message with optional context."""
        self._logger.debug(self._format_message(message, **context))

    def info(self, message: str, **context: ContextValue) -> None:
        """Log info message with optional context."""
        self._logger.info(self._format_message(message, **context))

    def warning(self, message: str, **context: ContextValue) -> None:
        """Log warning message with optional context."""
        self._logger.warning(self._format_message(message, **context))

    def error(self, message: str, **context: ContextValue) -> None:
        """Log error message with optional context."""
        self._logger.error(self._format_message(message, **context))

    def critical(self, message: str, **context: ContextValue) -> None:
        """Log critical message with optional context."""
        self._logger.critical(self._format_message(message, **context))

    def exception(self, message: str, **context: ContextValue) -> None:
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
