"""Service for updating status and publishing events."""

import logging
from typing import Any

from shared.messaging.publisher import RabbitMQPublisher
from shared.models import Document, Workspace
from shared.repositories.status import StatusRepository
from shared.types.result import Err, Ok, Result
from shared.types.status import DocumentProcessingStatus, WorkspaceStatus

logger = logging.getLogger(__name__)


class StatusService:
    """
    Service for updating document/workspace status and publishing events.
    
    This service coordinates status updates with event publishing,
    following the Single Responsibility Principle.
    """

    def __init__(
        self,
        status_repository: StatusRepository,
        message_publisher: RabbitMQPublisher | None = None,
    ):
        """
        Initialize status service.

        Args:
            status_repository: Repository for updating status
            message_publisher: Optional publisher for real-time events
        """
        self.status_repository = status_repository
        self.message_publisher = message_publisher

    def update_document_status(
        self,
        document_id: int,
        status: DocumentProcessingStatus,
        error: str | None = None,
        chunk_count: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Result[Document, str]:
        """
        Update document processing status and publish event.

        Args:
            document_id: Document ID
            status: New processing status
            error: Optional error message (for FAILED status)
            chunk_count: Optional chunk count (for READY status)
            metadata: Optional additional metadata for event

        Returns:
            Result containing Updated Document or error message
        """
        # Update status in database (returns Option[Document])
        doc_option = self.status_repository.update_document_status(
            document_id=document_id,
            status=status,
            error=error,
            chunk_count=chunk_count,
        )

        # Convert Option to Result
        if doc_option.is_nothing():
            logger.warning(f"Document {document_id} not found for status update")
            return Err(f"Document {document_id} not found")
        
        document = doc_option.unwrap()

        logger.info(f"Document {document_id} status updated to '{status.value}'")

        # Publish real-time event
        if self.message_publisher:
            event_data = {
                "document_id": document_id,
                "user_id": document.user_id,
                "workspace_id": document.workspace_id,
                "status": status.value,
                "error": error,
                "chunk_count": chunk_count,
                "filename": document.filename,
                "metadata": metadata or {},
            }
            self.message_publisher.publish(
                routing_key="document.status.updated",
                message=event_data,
            )
            logger.debug(f"Published document.status.updated event for document {document_id}")

        return Ok(document)

    def update_workspace_status(
        self,
        workspace_id: int,
        status: WorkspaceStatus,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Result[Workspace, str]:
        """
        Update workspace provisioning status and publish event.

        Args:
            workspace_id: Workspace ID
            status: New workspace status
            message: Optional status message
            metadata: Optional additional metadata for event

        Returns:
            Result containing Updated Workspace or error message
        """
        # Update status in database (returns Option[Workspace])
        ws_option = self.status_repository.update_workspace_status(
            workspace_id=workspace_id,
            status=status,
            message=message,
        )

        # Convert Option to Result
        if ws_option.is_nothing():
            logger.warning(f"Workspace {workspace_id} not found for status update")
            return Err(f"Workspace {workspace_id} not found")
        
        workspace = ws_option.unwrap()

        logger.info(f"Workspace {workspace_id} status updated to '{status.value}'")

        # Publish real-time event
        if self.message_publisher:
            event_data = {
                "workspace_id": workspace_id,
                "user_id": workspace.user_id,
                "status": status.value,
                "message": message,
                "name": workspace.name,
                "metadata": metadata or {},
            }
            self.message_publisher.publish(
                routing_key="workspace.status.updated",
                message=event_data,
            )
            logger.debug(f"Published workspace.status.updated event for workspace {workspace_id}")

        return Ok(workspace)
