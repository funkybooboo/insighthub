"""
Indexer Worker - Vector database indexing.

Consumes: embedding.created
Produces: document.indexed
"""

from dataclasses import asdict, dataclass
from typing import Any

from shared.config import config
from shared.workers import BaseWorker
from shared.logger import create_logger

logger = create_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
QDRANT_URL = f"http://{config.vector_store.qdrant_host}:{config.vector_store.qdrant_port}"
QDRANT_COLLECTION_NAME = config.vector_store.qdrant_collection_name
WORKER_CONCURRENCY = config.worker_concurrency


@dataclass
class DocumentIndexedEvent:
    """Event emitted when document is indexed."""

    document_id: str
    workspace_id: str
    vector_count: int
    collection_name: str
    metadata: dict[str, Any]


class IndexerWorker(BaseWorker):
    """Vector indexer worker."""

    def __init__(self) -> None:
        """Initialize the indexer worker."""
        super().__init__(
            worker_name="indexer",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="embedding.created",
            consume_queue="indexer.embedding.created",
            prefetch_count=WORKER_CONCURRENCY,
        )

        self._collection_name = QDRANT_COLLECTION_NAME

    def process_event(self, event_data: dict[str, Any], message_context: dict[str, Any]) -> None:
        """
        Process embedding.created event to index vectors.

        Args:
            event_data: Event data containing document_id, workspace_id, chunk_ids, etc.
            message_context: Message context information
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        chunk_ids = list(event_data.get("chunk_ids", []))
        embedding_count = int(event_data.get("embedding_count", 0))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Indexing vectors",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "vector_count": embedding_count,
                "collection_name": self._collection_name
            }
        )

        try:
            # TODO: Implement vector indexing
            # 1. Get embeddings from database
            # 2. Connect to Qdrant
            # 3. Upsert vectors with metadata
            # 4. Handle batching and errors

            vector_count = len(chunk_ids)  # Assume 1 vector per chunk

            # TODO: Update document status
            self._update_document_status(document_id, "indexed", {
                "vector_count": vector_count,
                "collection_name": self._collection_name
            })

            # Publish document.indexed event
            indexed_event = DocumentIndexedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                vector_count=vector_count,
                collection_name=self._collection_name,
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.indexed",
                event_data=asdict(indexed_event),
                correlation_id=message_context.get("correlation_id"),
                message_id=document_id,
            )

            logger.info(
                "Successfully indexed document",
                extra={
                    "document_id": document_id,
                    "vector_count": vector_count,
                    "collection_name": self._collection_name
                }
            )

        except Exception as e:
            logger.error(
                "Failed to index document",
                extra={
                    "document_id": document_id,
                    "error": str(e)
                }
            )
            # TODO: Update document status to failed
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _update_document_status(self, document_id: str, status: str, metadata: dict[str, Any] | None = None) -> None:
        """Update document processing status."""
        # TODO: Implement status update
        # 1. Connect to PostgreSQL
        # 2. Update processing_status and processing_metadata
        # 3. Handle connection errors
        pass


def main() -> None:
    """Main entry point."""
    worker = IndexerWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping indexer worker")
        worker.stop()


if __name__ == "__main__":
    main()