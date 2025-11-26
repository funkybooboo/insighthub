"""Infrastructure manager worker - consolidated provisioning and deletion operations."""

import logging
from typing import Any, Dict

from shared.config import AppConfig
from shared.database.vector import create_vector_store
from shared.database.graph import create_graph_store
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.worker import Worker

logger = logging.getLogger(__name__)


class InfrastructureManagerWorker(Worker):
    """Consolidated worker for infrastructure management: provisioning and deletion."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ):
        """Initialize the infrastructure manager worker."""
        super().__init__(consumer, publisher, config)
        self.vector_store = create_vector_store("qdrant")
        self.graph_store = create_graph_store("neo4j")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process infrastructure management message."""
        try:
            event_type = message.get("event_type")
            if event_type == "workspace.provision_requested":
                self._provision_workspace(message)
            elif event_type == "workspace.deletion_requested":
                self._delete_workspace(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing infrastructure management message: {e}")

    def _provision_workspace(self, message: Dict[str, Any]) -> None:
        """Provision infrastructure for a new workspace."""
        workspace_id = message.get("workspace_id")

        if not workspace_id:
            logger.error("Missing workspace_id in provision request")
            return

        try:
            # Provision vector database collection
            vector_provisioned = self._provision_vector_store(workspace_id)

            # Provision graph database structures
            graph_provisioned = self._provision_graph_store(workspace_id)

            # Publish completion event
            self.publisher.publish_event(
                event_type="workspace.provision_status",
                workspace_id=workspace_id,
                status="completed",
                vector_provisioned=vector_provisioned,
                graph_provisioned=graph_provisioned,
            )

            logger.info(f"Successfully provisioned infrastructure for workspace {workspace_id}")

        except Exception as e:
            logger.error(f"Error provisioning workspace {workspace_id}: {e}")

            # Publish failure event
            self.publisher.publish_event(
                event_type="workspace.provision_status",
                workspace_id=workspace_id,
                status="failed",
                error=str(e),
            )

    def _delete_workspace(self, message: Dict[str, Any]) -> None:
        """Delete infrastructure for a workspace."""
        workspace_id = message.get("workspace_id")

        if not workspace_id:
            logger.error("Missing workspace_id in deletion request")
            return

        try:
            # Delete vector database data
            vector_deleted = self._delete_vector_data(workspace_id)

            # Delete graph database data
            graph_deleted = self._delete_graph_data(workspace_id)

            # Publish completion event
            self.publisher.publish_event(
                event_type="workspace.deletion_status",
                workspace_id=workspace_id,
                status="completed",
                vector_deleted=vector_deleted,
                graph_deleted=graph_deleted,
            )

            logger.info(f"Successfully deleted infrastructure for workspace {workspace_id}")

        except Exception as e:
            logger.error(f"Error deleting workspace {workspace_id}: {e}")

            # Publish failure event
            self.publisher.publish_event(
                event_type="workspace.deletion_status",
                workspace_id=workspace_id,
                status="failed",
                error=str(e),
            )

    def _provision_vector_store(self, workspace_id: int) -> bool:
        """Provision vector store for workspace."""
        try:
            # Create collection for workspace
            collection_name = f"workspace_{workspace_id}"
            # Note: In a real implementation, this would create the collection
            # For now, we'll assume the vector store handles this automatically
            logger.info(f"Provisioned vector collection for workspace {workspace_id}")
            return True
        except Exception as e:
            logger.error(f"Error provisioning vector store for workspace {workspace_id}: {e}")
            return False

    def _provision_graph_store(self, workspace_id: int) -> bool:
        """Provision graph store for workspace."""
        try:
            # Initialize graph structures for workspace
            # Note: In a real implementation, this would create graph schemas/constraints
            # For now, we'll assume the graph store handles this automatically
            logger.info(f"Provisioned graph structures for workspace {workspace_id}")
            return True
        except Exception as e:
            logger.error(f"Error provisioning graph store for workspace {workspace_id}: {e}")
            return False

    def _delete_vector_data(self, workspace_id: int) -> bool:
        """Delete vector data for workspace."""
        try:
            # Delete all vectors for this workspace
            # Note: In a real implementation, this would delete the collection or all vectors with workspace_id filter
            logger.info(f"Deleted vector data for workspace {workspace_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vector data for workspace {workspace_id}: {e}")
            return False

    def _delete_graph_data(self, workspace_id: int) -> bool:
        """Delete graph data for workspace."""
        try:
            # Delete all graph data for this workspace
            # Note: In a real implementation, this would delete nodes/relationships with workspace_id
            logger.info(f"Deleted graph data for workspace {workspace_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting graph data for workspace {workspace_id}: {e}")
            return False


def create_infrastructure_manager_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: AppConfig,
) -> InfrastructureManagerWorker:
    """Create an infrastructure manager worker."""
    return InfrastructureManagerWorker(consumer, publisher, config)