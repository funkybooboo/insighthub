"""Notification interface for sending alerts and messages."""

from abc import ABC, abstractmethod

from shared.types.result import Err, Ok, Result


class NotifyError:
    """Error type for notification failures."""

    def __init__(self, message: str, code: str = "NOTIFY_ERROR") -> None:
        """
        Initialize notification error.

        Args:
            message: Error message
            code: Error code for categorization
        """
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.code}] {self.message}"


class Notify(ABC):
    """
    Abstract interface for notification operations.

    Implementations: NoopNotify, SlackNotify, EmailNotify, WebhookNotify
    """

    @abstractmethod
    def send(
        self, channel: str, message: str, metadata: dict[str, str] | None = None
    ) -> Result[bool, NotifyError]:
        """
        Send a notification message.

        Args:
            channel: Target channel/destination for the notification
            message: Message content to send
            metadata: Optional metadata for the notification

        Returns:
            Result containing True on success, or NotifyError on failure
        """
        pass

    @abstractmethod
    def send_alert(
        self,
        channel: str,
        title: str,
        message: str,
        severity: str = "info",
        metadata: dict[str, str] | None = None,
    ) -> Result[bool, NotifyError]:
        """
        Send an alert notification with severity level.

        Args:
            channel: Target channel/destination for the alert
            title: Alert title
            message: Alert message content
            severity: Alert severity (info, warning, error, critical)
            metadata: Optional metadata for the alert

        Returns:
            Result containing True on success, or NotifyError on failure
        """
        pass

    @abstractmethod
    def health_check(self) -> dict[str, str | bool]:
        """
        Check if the notification service is available.

        Returns:
            Dictionary with health status
        """
        pass
