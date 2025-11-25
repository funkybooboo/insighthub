"""
Provisioner Worker - Workspace infrastructure provisioning.

Consumes: workspace.provision_requested
Produces: workspace.provision_status
"""

import os
from dataclasses import asdict, dataclass
from typing import Any

import pika
from qdrant_client import QdrantClient
from qdrant_client.http import models
import psycopg2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insighthub:insighthub_dev@postgres:5432/insighthub")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))


@dataclass
class WorkspaceProvisionStatusEvent:
    """Event emitted during workspace provisioning."""

    workspace_id: str
    user_id: str
    status: str  # 'provisioning', 'ready', 'failed'
    message: str
    metadata: dict[str, Any]


class Worker:
    """Base worker class for RabbitMQ message processing."""

    def __init__(
        self,
        worker_name: str,
        rabbitmq_url: str,
        exchange: str,
        exchange_type: str,
        consume_routing_key: str,
        consume_queue: str,
        prefetch_count: int = 1,
    ):
        self.worker_name = worker_name
        self.rabbitmq_url = rabbitmq_url
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.consume_routing_key = consume_routing_key
        self.consume_queue = consume_queue
        self.prefetch_count = prefetch_count
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.channel.Channel | None = None

    def start(self) -> None:
        """Start the worker."""
        self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        self.channel = self.connection.channel()

        # Declare exchange
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type,
            durable=True
        )

        # Declare queue
        self.channel.queue_declare(queue=self.consume_queue, durable=True)
        self.channel.queue_bind(
            exchange=self.exchange,
            queue=self.consume_queue,
            routing_key=self.consume_routing_key
        )

        # Set prefetch count
        self.channel.basic_qos(prefetch_count=self.prefetch_count)

        # Start consuming
        self.channel.basic_consume(
            queue=self.consume_queue,
            on_message_callback=self._on_message
        )

        logger.info(f"Started {self.worker_name} worker")
        self.channel.start_consuming()

    def stop(self) -> None:
        """Stop the worker."""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()

    def _on_message(
        self,
        ch: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes
    ) -> None:
        """Handle incoming message."""
        try:
            import json
            event_data = json.loads(body.decode('utf-8'))
            self.process_event(event_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def process_event(self, event_data: dict[str, Any]) -> None:
        """Process the event. Override in subclasses."""
        raise NotImplementedError

    def publish_event(self, routing_key: str, event_data: dict[str, Any]) -> None:
        """Publish an event to RabbitMQ."""
        if not self.channel:
            raise RuntimeError("Worker not started")

        import json
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=json.dumps(event_data).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )


def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(DATABASE_URL)


class VectorStoreProvisioner:
    """Provisions vector stores for workspaces."""

    def __init__(self, qdrant_url: str):
        self.qdrant_url = qdrant_url
        self.client = QdrantClient(url=qdrant_url)

    def provision_workspace_collection(self, workspace_id: str, rag_config: dict[str, Any]) -> str:
        """
        Provision a Qdrant collection for the workspace.

        Args:
            workspace_id: Workspace ID
            rag_config: RAG configuration

        Returns:
            Collection name
        """
        collection_name = f"workspace_{workspace_id}"

        # Get embedding dimension from config or use default
        embedding_model = rag_config.get("embedding_model", "nomic-embed-text")
        embedding_dim = rag_config.get("embedding_dim", 768)  # Default for nomic-embed-text

        try:
            # Check if collection exists
            self.client.get_collection(collection_name)
            logger.info(f"Collection {collection_name} already exists")
        except Exception:
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_dim,
                    distance=models.Distance.COSINE
                ),
                # Enable payload indexing for metadata filtering
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=0  # Index all vectors immediately
                )
            )
            logger.info(f"Created collection {collection_name} with vector size {embedding_dim}")

        return collection_name


class GraphStoreProvisioner:
    """Provisions graph stores for workspaces."""

    def __init__(self, neo4j_url: str):
        self.neo4j_url = neo4j_url
        # TODO: Initialize Neo4j driver when graph RAG is implemented
        self.driver = None

    def provision_workspace_graph(self, workspace_id: str, rag_config: dict[str, Any]) -> str:
        """
        Provision a Neo4j graph database for the workspace.

        Args:
            workspace_id: Workspace ID
            rag_config: RAG configuration

        Returns:
            Graph name/identifier
        """
        graph_name = f"workspace_{workspace_id}_graph"

        # TODO: Implement Neo4j graph provisioning when graph RAG is added
        logger.info(f"Graph provisioning not yet implemented for {graph_name}")

        return graph_name


class ProvisionerWorker(Worker):
    """Workspace provisioner worker."""

    def __init__(self) -> None:
        """Initialize the provisioner worker."""
        super().__init__(
            worker_name="provisioner",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="workspace.provision_requested",
            consume_queue="provisioner.workspace.provision_requested",
            prefetch_count=WORKER_CONCURRENCY,
        )

        # Initialize provisioners
        self.vector_provisioner = VectorStoreProvisioner(QDRANT_URL)
        self.graph_provisioner = GraphStoreProvisioner("bolt://neo4j:7687")  # Placeholder

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process workspace.provision_requested event.

        Args:
            event_data: Event data containing workspace_id, rag_config, etc.
        """
        workspace_id = str(event_data.get("workspace_id", ""))
        user_id = str(event_data.get("user_id", ""))
        rag_config = event_data.get("rag_config", {})

        logger.info(
            "Provisioning workspace infrastructure",
            extra={
                "workspace_id": workspace_id,
                "user_id": user_id,
                "retriever_type": rag_config.get("retriever_type", "vector")
            }
        )

        try:
            # Update workspace status to provisioning
            self._update_workspace_status(workspace_id, "provisioning", "Initializing workspace resources...")

            # Publish initial status event
            self._publish_status_event(workspace_id, user_id, "provisioning", "Starting provisioning...")

            retriever_type = rag_config.get("retriever_type", "vector")

            # Provision vector store (always needed)
            collection_name = self.vector_provisioner.provision_workspace_collection(workspace_id, rag_config)

            # Provision graph store if needed
            graph_name = None
            if retriever_type in ["graph", "hybrid"]:
                graph_name = self.graph_provisioner.provision_workspace_graph(workspace_id, rag_config)

            # Update workspace with provisioned resource names
            self._update_workspace_resources(workspace_id, collection_name, graph_name)

            # Update workspace status to ready
            self._update_workspace_status(workspace_id, "ready", "Workspace provisioning completed")

            # Publish final status event
            self._publish_status_event(workspace_id, user_id, "ready", "Workspace ready for use")

            logger.info(
                "Successfully provisioned workspace",
                extra={
                    "workspace_id": workspace_id,
                    "collection_name": collection_name
                }
            )

        except Exception as e:
            logger.error(
                "Failed to provision workspace",
                extra={
                    "workspace_id": workspace_id,
                    "error": str(e)
                }
            )
            # Update workspace status to failed
            self._update_workspace_status(workspace_id, "failed", f"Provisioning failed: {str(e)}")

            # Publish failure status event
            self._publish_status_event(workspace_id, user_id, "failed", f"Provisioning failed: {str(e)}")
            raise

    def _update_workspace_status(self, workspace_id: str, status: str, message: str) -> None:
        """Update workspace status in database."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE workspaces
                    SET status = %s, status_message = %s, updated_at = NOW()
                    WHERE id = %s
                """, (status, message, workspace_id))
            conn.commit()
        finally:
            conn.close()

    def _update_workspace_resources(self, workspace_id: str, collection_name: str, graph_name: str | None) -> None:
        """Update workspace with provisioned resource names."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE workspaces
                    SET rag_collection = %s, updated_at = NOW()
                    WHERE id = %s
                """, (collection_name, workspace_id))
            conn.commit()
        finally:
            conn.close()

    def _publish_status_event(self, workspace_id: str, user_id: str, status: str, message: str) -> None:
        """Publish workspace provision status event."""
        event = WorkspaceProvisionStatusEvent(
            workspace_id=workspace_id,
            user_id=user_id,
            status=status,
            message=message,
            metadata={}
        )
        self.publish_event("workspace.provision_status", asdict(event))


def main() -> None:
    """Main entry point."""
    worker = ProvisionerWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping provisioner worker")
        worker.stop()


if __name__ == "__main__":
    main()