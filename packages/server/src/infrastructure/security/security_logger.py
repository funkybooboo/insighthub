"""Security event logging."""

from typing import Any

from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def log_security_event(
    event: str,
    user_id: int | None = None,
    client_ip: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Log a security event with structured information.

    Args:
        event: The security event type (e.g., "login_successful", "login_failed")
        user_id: The user ID associated with the event (optional)
        client_ip: The client IP address (optional)
        details: Additional details about the event (optional)
    """
    log_data = {
        "event": event,
        "user_id": user_id,
        "client_ip": client_ip,
    }

    if details:
        log_data["details"] = details

    logger.info(f"Security event: {event}", extra=log_data)