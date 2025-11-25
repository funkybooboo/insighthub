"""
Deletion Worker - Workspace and document cleanup.

Consumes: workspace.deletion_requested, document.deleted
Produces: workspace.deletion_status
"""

import os
from dataclasses import asdict, dataclass
from typing import Any

from shared.workers import BaseWorker
from shared.logger import create_logger

logger = create_logger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insighthub:insighthub_dev@postgres:5432/insighthub")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "2"))


@dataclass
class WorkspaceDeletionStatusEvent:
    """Event emitted when workspace deletion status changes."""

    workspace_id: str
    status: str  # "deleting", "completed", "failed"
    message: str
    progress_percentage: int
    metadata: dict[str, Any]


class DeletionWorker(BaseWorker):
    """Deletion worker for cleaning up workspaces and documents."""

    def __init__(self) -> None:
        """Initialize the deletion worker."""
        super().__init__(
            worker_name="deletion",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="workspace.deletion_requested",  # Also listen to document.deleted
            consume_queue="deletion.workspace.deletion_requested",
            prefetch_count=WORKER_CONCURRENCY,
        )

    def process_event(self, event_data: dict[str, Any], message_context: dict[str, Any]) -> None:
        """
        Process workspace.deletion_requested or document.deleted events.

        Args:
            event_data: Event data containing workspace_id or document_id
            message_context: Message context information
        """
        # Check if this is a workspace deletion or document deletion
        if "workspace_id" in event_data:
            self._handle_workspace_deletion(event_data, message_context)
        elif "document_id" in event_data:
            self._handle_document_deletion(event_data, message_context)
        else:
            logger.error("Unknown deletion event type", extra={"event_data": event_data})

    def _handle_workspace_deletion(self, event_data: dict[str, Any], message_context: dict[str, Any]) -> None:
        """
        Handle workspace deletion request.

        Args:
            event_data: Workspace deletion event data
            message_context: Message context information
        """
        workspace_id = str(event_data.get("workspace_id", ""))
        workspace_name = str(event_data.get("name", ""))

        logger.info(
            "Starting workspace deletion",
            extra={
                "workspace_id": workspace_id,
                "workspace_name": workspace_name
            }
        )

        try:
            # Update status to deleting
            self._publish_deletion_status(
                workspace_id=workspace_id,
                status="deleting",
                message="Starting workspace deletion",
                progress_percentage=0,
                message_context=message_context
            )

            # TODO: Implement workspace deletion steps
            # 1. Delete all documents in the workspace
            # 2. Delete vector collections from Qdrant
            # 3. Delete graph data from Neo4j
            # 4. Delete MinIO buckets/objects
            # 5. Delete database records
            # 6. Update progress status

            # Simulate deletion steps with progress updates
            steps = [
                ("Deleting documents", 20),
                ("Cleaning vector database", 40),
                ("Cleaning graph database", 60),
                ("Cleaning object storage", 80),
                ("Finalizing deletion", 100)
            ]

            for step_message, progress in steps:
                self._publish_deletion_status(
                    workspace_id=workspace_id,
                    status="deleting",
                    message=step_message,
                    progress_percentage=progress,
                    message_context=message_context
                )
                # TODO: Actually perform the deletion step

            # Mark as completed
            self._publish_deletion_status(
                workspace_id=workspace_id,
                status="completed",
                message="Workspace deletion completed successfully",
                progress_percentage=100,
                message_context=message_context
            )

            logger.info(
                "Workspace deletion completed",
                extra={"workspace_id": workspace_id}
            )

        except Exception as e:
            logger.error(
                "Workspace deletion failed",
                extra={
                    "workspace_id": workspace_id,
                    "error": str(e)
                }
            )
            # Publish failure status
            self._publish_deletion_status(
                workspace_id=workspace_id,
                status="failed",
                message=f"Workspace deletion failed: {str(e)}",
                progress_percentage=0,
                message_context=message_context
            )
            raise

    def _handle_document_deletion(self, event_data: dict[str, Any], message_context: dict[str, Any]) -> None:
        """
        Handle document deletion request.

        Args:
            event_data: Document deletion event data
            message_context: Message context information
        """
        document_id = str(event_data.get("document_id", ""))

        logger.info(
            "Deleting document",
            extra={"document_id": document_id}
        )

        try:
            # TODO: Implement document deletion
            # 1. Delete document chunks from database
            # 2. Delete vectors from Qdrant
            # 3. Delete graph nodes from Neo4j
            # 4. Delete file from MinIO
            # 5. Delete document record from database

            logger.info(
                "Document deletion completed",
                extra={"document_id": document_id}
            )

        except Exception as e:
            logger.error(
                "Document deletion failed",
                extra={
                    "document_id": document_id,
                    "error": str(e)
                }
            )
            raise

    def _publish_deletion_status(
        self,
        workspace_id: str,
        status: str,
        message: str,
        progress_percentage: int,
        message_context: dict[str, Any]
    ) -> None:
        """Publish workspace deletion status update."""
        event = WorkspaceDeletionStatusEvent(
            workspace_id=workspace_id,
            status=status,
            message=message,
            progress_percentage=progress_percentage,
            metadata={}
        )

        self.publish_event(
            routing_key="workspace.deletion_status",
            event_data=asdict(event),
            correlation_id=message_context.get("correlation_id"),
            message_id=workspace_id,
        )


def main() -> None:
    """Main entry point."""
    worker = DeletionWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping deletion worker")
        worker.stop()


if __name__ == "__main__":
    main()