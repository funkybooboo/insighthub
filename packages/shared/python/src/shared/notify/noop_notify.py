"""No-operation notify implementation for testing and development."""

from shared.logger import create_logger
from shared.types.result import Ok, Result

from .notify import Notify, NotifyError

logger = create_logger(__name__)


class NoopNotify(Notify):
    """
    No-operation notify implementation.

    Logs notifications without actually sending them.
    Used for testing and development environments.

    Example:
        notify = NoopNotify()
        result = notify.send("general", "Hello, world!")
        if result.is_ok():
            print("Notification logged successfully")
    """

    def send(
        self, channel: str, message: str, metadata: dict[str, str] | None = None
    ) -> Result[bool, NotifyError]:
        """
        Log a notification message without sending.

        Args:
            channel: Target channel/destination (logged only)
            message: Message content (logged only)
            metadata: Optional metadata (logged only)

        Returns:
            Result containing True (always succeeds)
        """
        logger.info(
            "NoopNotify: would send notification",
            channel=channel,
            message=message[:100] if len(message) > 100 else message,
            has_metadata=metadata is not None,
        )
        return Ok(True)

    def send_alert(
        self,
        channel: str,
        title: str,
        message: str,
        severity: str = "info",
        metadata: dict[str, str] | None = None,
    ) -> Result[bool, NotifyError]:
        """
        Log an alert notification without sending.

        Args:
            channel: Target channel/destination (logged only)
            title: Alert title (logged only)
            message: Alert message content (logged only)
            severity: Alert severity level (logged only)
            metadata: Optional metadata (logged only)

        Returns:
            Result containing True (always succeeds)
        """
        logger.info(
            "NoopNotify: would send alert",
            channel=channel,
            title=title,
            severity=severity,
            message=message[:100] if len(message) > 100 else message,
            has_metadata=metadata is not None,
        )
        return Ok(True)

    def health_check(self) -> dict[str, str | bool]:
        """
        Return healthy status (always available).

        Returns:
            Dictionary with health status
        """
        return {
            "status": "healthy",
            "provider": "noop",
        }
