"""Factory for creating notification service instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

from .notify import Notify
from .noop_notify import NoopNotify


class NotifyType(Enum):
    """Enum for notification implementation types."""

    NOOP = "noop"


def create_notify(
    notify_type: str,
) -> Option[Notify]:
    """
    Create a notification service instance based on configuration.

    Args:
        notify_type: Type of notification service ("noop")

    Returns:
        Some(Notify) if creation succeeds, Nothing() if type unknown

    Note:
        Additional notification providers (Slack, Email, Webhook) can be
        added here when implemented.
    """
    try:
        notify_enum = NotifyType(notify_type)
    except ValueError:
        return Nothing()

    if notify_enum == NotifyType.NOOP:
        return Some(NoopNotify())

    return Nothing()
