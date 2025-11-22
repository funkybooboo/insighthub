"""Status publisher for broadcasting status updates via RabbitMQ."""

import os
from dataclasses import asdict

from shared.logger import create_logger

from .events.status import DocumentStatusEvent, WorkspaceStatusEvent
from .publisher import RabbitMQPublisher

logger = create_logger(__name__)

# Routing keys for status updates
DOCUMENT_STATUS_KEY = "document.status.updated"
WORKSPACE_STATUS_KEY = "workspace.status.updated"


class StatusPublisher:
    """
    Publisher for broadcasting document and workspace status updates.

    Uses RabbitMQ to publish status events that are consumed by the
    status consumer and forwarded to Socket.IO clients.
    """

    def __init__(self, publisher: RabbitMQPublisher) -> None:
        """
        Initialize the status publisher.

        Args:
            publisher: RabbitMQ publisher instance (must be connected)
        """
        self._publisher = publisher

    def publish_document_status(
        self,
        document_id: int,
        workspace_id: int,
        status: str,
        message: str | None = None,
        error: str | None = None,
        progress: int | None = None,
    ) -> None:
        """
        Publish a document status update.

        Args:
            document_id: Document ID
            workspace_id: Workspace ID the document belongs to
            status: New status ('pending', 'processing', 'ready', 'failed')
            message: Optional status message
            error: Optional error message for failed status
            progress: Optional progress percentage (0-100)
        """
        event = DocumentStatusEvent(
            document_id=document_id,
            workspace_id=workspace_id,
            status=status,
            message=message,
            error=error,
            progress=progress,
        )

        try:
            self._publisher.publish(DOCUMENT_STATUS_KEY, asdict(event))
            logger.info(
                "Published document status",
                document_id=document_id,
                status=status,
            )
        except Exception as e:
            logger.error(
                "Failed to publish document status",
                document_id=document_id,
                error=str(e),
            )

    def publish_workspace_status(
        self,
        workspace_id: int,
        user_id: int,
        status: str,
        message: str | None = None,
        error: str | None = None,
    ) -> None:
        """
        Publish a workspace status update.

        Args:
            workspace_id: Workspace ID
            user_id: User ID who owns the workspace
            status: New status ('provisioning', 'ready', 'error')
            message: Optional status message
            error: Optional error message for error status
        """
        event = WorkspaceStatusEvent(
            workspace_id=workspace_id,
            user_id=user_id,
            status=status,
            message=message,
            error=error,
        )

        try:
            self._publisher.publish(WORKSPACE_STATUS_KEY, asdict(event))
            logger.info(
                "Published workspace status",
                workspace_id=workspace_id,
                status=status,
            )
        except Exception as e:
            logger.error(
                "Failed to publish workspace status",
                workspace_id=workspace_id,
                error=str(e),
            )


def create_status_publisher() -> StatusPublisher | None:
    """
    Create a status publisher from environment configuration.

    Returns:
        StatusPublisher if RabbitMQ is configured, None otherwise
    """
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "guest")
    exchange = os.getenv("RABBITMQ_EXCHANGE", "insighthub")

    if not rabbitmq_host:
        logger.info("RabbitMQ not configured, status publisher disabled")
        return None

    try:
        publisher = RabbitMQPublisher(
            host=rabbitmq_host,
            port=rabbitmq_port,
            username=rabbitmq_user,
            password=rabbitmq_pass,
            exchange=exchange,
            exchange_type="topic",
        )
        publisher.connect()

        return StatusPublisher(publisher)
    except Exception as e:
        logger.error(f"Failed to create status publisher: {e}")
        return None


# Global status publisher instance (initialized lazily)
_status_publisher: StatusPublisher | None = None


def get_status_publisher() -> StatusPublisher | None:
    """
    Get or create the global status publisher instance.

    Returns:
        StatusPublisher if available, None otherwise
    """
    global _status_publisher
    if _status_publisher is None:
        _status_publisher = create_status_publisher()
    return _status_publisher


def publish_document_status(
    document_id: int,
    workspace_id: int,
    status: str,
    message: str | None = None,
    error: str | None = None,
    progress: int | None = None,
) -> None:
    """
    Convenience function to publish document status using global publisher.

    Args:
        document_id: Document ID
        workspace_id: Workspace ID
        status: New status
        message: Optional status message
        error: Optional error message
        progress: Optional progress percentage
    """
    publisher = get_status_publisher()
    if publisher:
        publisher.publish_document_status(
            document_id=document_id,
            workspace_id=workspace_id,
            status=status,
            message=message,
            error=error,
            progress=progress,
        )


def publish_workspace_status(
    workspace_id: int,
    user_id: int,
    status: str,
    message: str | None = None,
    error: str | None = None,
) -> None:
    """
    Convenience function to publish workspace status using global publisher.

    Args:
        workspace_id: Workspace ID
        user_id: User ID
        status: New status
        message: Optional status message
        error: Optional error message
    """
    publisher = get_status_publisher()
    if publisher:
        publisher.publish_workspace_status(
            workspace_id=workspace_id,
            user_id=user_id,
            status=status,
            message=message,
            error=error,
        )
