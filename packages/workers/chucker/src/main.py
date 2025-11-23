"""
Chucker Worker - Document chunking for embeddings.

Consumes: document.parsed
Produces: document.chunked
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
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))


@dataclass
class DocumentChunkedEvent:
    """Event emitted when document is chunked."""

    document_id: str
    workspace_id: str
    chunk_ids: list[str]
    chunk_count: int
    metadata: dict[str, str]


class ChuckerWorker(Worker):
    """Document chunker worker."""

    def __init__(self) -> None:
        """Initialize the chucker worker."""
        super().__init__(
            worker_name="chucker",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.parsed",
            consume_queue="chucker.document.parsed",
            prefetch_count=WORKER_CONCURRENCY,
        )
        self._database_url = DATABASE_URL
        self._chunk_size = CHUNK_SIZE
        self._chunk_overlap = CHUNK_OVERLAP

    def process_event(self, event_data: PayloadDict) -> None:
        """
        Process document.parsed event to create chunks.

        TODO: Implement chunking logic:
        1. Fetch parsed text from database
        2. Split into chunks using configured strategy
        3. Store chunks in database
        4. Publish document.chunked event

        Args:
            event_data: Parsed event data as dictionary
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        metadata = dict(event_data.get("metadata", {}))

        logger.info(
            "Chunking document",
            document_id=document_id,
            workspace_id=workspace_id,
            chunk_size=self._chunk_size,
        )

        try:
            # TODO: Implement chunking
            chunk_ids: list[str] = []

            # Publish document.chunked event
            chunked_event = DocumentChunkedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                chunk_ids=chunk_ids,
                chunk_count=len(chunk_ids),
                metadata=metadata,
            )
            self.publish_event("document.chunked", asdict(chunked_event))

            logger.info(
                "Successfully chunked document",
                document_id=document_id,
                chunk_count=len(chunk_ids),
            )

        except Exception as e:
            logger.error(
                "Failed to chunk document",
                document_id=document_id,
                error=str(e),
            )
            raise


def main() -> None:
    """Main entry point."""
    worker = ChuckerWorker()
    worker.start()


if __name__ == "__main__":
    main()
