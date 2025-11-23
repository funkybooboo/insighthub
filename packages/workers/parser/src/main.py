"""
Parser Worker - Document text extraction.

Consumes: document.ingested
Produces: document.parsed
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
MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "insighthub")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "insighthub_dev_secret")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "documents")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))


@dataclass
class DocumentParsedEvent:
    """Event emitted when document is parsed."""

    document_id: str
    workspace_id: str
    content_type: str
    text_length: int
    metadata: dict[str, str]


class ParserWorker(Worker):
    """Document parser worker."""

    def __init__(self) -> None:
        """Initialize the parser worker."""
        super().__init__(
            worker_name="parser",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.ingested",
            consume_queue="parser.document.ingested",
            prefetch_count=WORKER_CONCURRENCY,
        )
        self._database_url = DATABASE_URL
        self._minio_endpoint = MINIO_ENDPOINT_URL
        self._minio_access_key = MINIO_ACCESS_KEY
        self._minio_secret_key = MINIO_SECRET_KEY
        self._minio_bucket = MINIO_BUCKET_NAME

    def process_event(self, event_data: PayloadDict) -> None:
        """
        Process document.ingested event to extract text.

        TODO: Implement parsing logic:
        1. Fetch document from MinIO storage
        2. Detect content type (PDF, DOCX, HTML, TXT)
        3. Extract text using appropriate parser
        4. Store parsed text in database
        5. Publish document.parsed event

        Args:
            event_data: Parsed event data as dictionary
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        content_type = str(event_data.get("content_type", "text/plain"))
        metadata = dict(event_data.get("metadata", {}))

        logger.info(
            "Parsing document",
            document_id=document_id,
            workspace_id=workspace_id,
            content_type=content_type,
        )

        try:
            # TODO: Implement parsing
            text_length = 0

            # Publish document.parsed event
            parsed_event = DocumentParsedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                content_type=content_type,
                text_length=text_length,
                metadata=metadata,
            )
            self.publish_event("document.parsed", asdict(parsed_event))

            logger.info(
                "Successfully parsed document",
                document_id=document_id,
                text_length=text_length,
            )

        except Exception as e:
            logger.error(
                "Failed to parse document",
                document_id=document_id,
                error=str(e),
            )
            raise


def main() -> None:
    """Main entry point."""
    worker = ParserWorker()
    worker.start()


if __name__ == "__main__":
    main()
