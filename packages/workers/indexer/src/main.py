"""
Indexer Worker - Vector database indexing.

Consumes: embedding.created
Produces: vector.indexed
"""

import os
from dataclasses import asdict, dataclass

from shared.logger import create_logger
from shared.types.common import PayloadDict
from shared.worker import Worker

logger = create_logger(__name__)

# Environment variables
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://insighthub:insighthub_dev@postgres:5432/insighthub")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "documents")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "2"))


@dataclass
class VectorIndexedEvent:
    """Event emitted when vectors are indexed."""

    document_id: str
    workspace_id: str
    vector_count: int
    collection_name: str
    metadata: dict[str, str]


class IndexerWorker(Worker):
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
        self._database_url = DATABASE_URL
        self._qdrant_url = QDRANT_URL
        self._collection_name = QDRANT_COLLECTION_NAME

    def process_event(self, event_data: PayloadDict) -> None:
        """
        Process embedding.created event to index vectors.

        TODO: Implement indexing logic:
        1. Fetch embeddings from database
        2. Upsert vectors to Qdrant with metadata
        3. Publish vector.indexed event

        Args:
            event_data: Parsed event data as dictionary
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        metadata = dict(event_data.get("metadata", {}))

        logger.info(
            "Indexing vectors",
            document_id=document_id,
            workspace_id=workspace_id,
            collection=self._collection_name,
        )

        try:
            # TODO: Implement vector indexing
            vector_count = 0

            # Publish vector.indexed event
            indexed_event = VectorIndexedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                vector_count=vector_count,
                collection_name=self._collection_name,
                metadata=metadata,
            )
            self.publish_event("vector.indexed", asdict(indexed_event))

            logger.info(
                "Successfully indexed vectors",
                document_id=document_id,
                vector_count=vector_count,
            )

        except Exception as e:
            logger.error(
                "Failed to index vectors",
                document_id=document_id,
                error=str(e),
            )
            raise


def main() -> None:
    """Main entry point."""
    worker = IndexerWorker()
    worker.start()


if __name__ == "__main__":
    main()
