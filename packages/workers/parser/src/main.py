"""
Parser Worker - Document text extraction.

Consumes: document.uploaded
Produces: document.parsed
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
MINIO_ENDPOINT_URL = config.storage.s3_endpoint_url
MINIO_ACCESS_KEY = config.storage.s3_access_key
MINIO_SECRET_KEY = config.storage.s3_secret_key
MINIO_BUCKET_NAME = config.storage.s3_bucket_name
WORKER_CONCURRENCY = config.worker_concurrency


@dataclass
class DocumentParsedEvent:
    """Event emitted when document is parsed."""

    document_id: str
    workspace_id: str
    content_type: str
    text_length: int
    metadata: dict[str, Any]


class DocumentParser:
    """Document parser for various file formats."""

    def __init__(self):
        """Initialize the document parser."""
        # TODO: Initialize MinIO client
        # self.minio_client = Minio(...)
        pass

    def parse_document(self, document_id: str, content_type: str, file_path: str) -> str:
        """
        Parse document content based on content type.

        Args:
            document_id: Document ID
            content_type: MIME content type
            file_path: Path to file in MinIO

        Returns:
            Extracted text content
        """
        # TODO: Implement document parsing logic
        # 1. Retrieve file from MinIO
        # 2. Parse based on content type (PDF, DOCX, HTML, TXT)
        # 3. Return extracted text

        # Placeholder implementation
        return f"Parsed content for document {document_id}"


class ParserWorker(BaseWorker):
    """Document parser worker."""

    def __init__(self) -> None:
        """Initialize the parser worker."""
        super().__init__(
            worker_name="parser",
            rabbitmq_url=config.rabbitmq_url,
            exchange=config.rabbitmq_exchange,
            exchange_type="topic",
            consume_routing_key="document.uploaded",
            consume_queue="parser.document.uploaded",
            prefetch_count=config.worker_concurrency,
        )

        # Initialize document parser
        self.parser = DocumentParser()

    def process_event(self, event_data: dict[str, Any], message_context: dict[str, Any]) -> None:
        """
        Process document.uploaded event to extract text.

        Args:
            event_data: Event data containing document_id, workspace_id, content_type, file_path, etc.
            message_context: Message context information
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        content_type = str(event_data.get("content_type", "text/plain"))
        file_path = str(event_data.get("file_path", ""))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Parsing document",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "content_type": content_type,
                "file_path": file_path
            }
        )

        try:
            # Parse the document
            text_content = self.parser.parse_document(document_id, content_type, file_path)
            text_length = len(text_content)

            # TODO: Store parsed text in database
            self._store_parsed_text(document_id, text_content)

            # TODO: Update document status
            self._update_document_status(document_id, "parsed", {"text_length": text_length})

            # Publish document.parsed event
            parsed_event = DocumentParsedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                content_type=content_type,
                text_length=text_length,
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.parsed",
                event_data=asdict(parsed_event),
                correlation_id=message_context.get("correlation_id"),
                message_id=document_id,
            )

            logger.info(
                "Successfully parsed document",
                extra={
                    "document_id": document_id,
                    "text_length": text_length
                }
            )

        except Exception as e:
            logger.error(
                "Failed to parse document",
                extra={
                    "document_id": document_id,
                    "error": str(e)
                }
            )
            # TODO: Update document status to failed
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _store_parsed_text(self, document_id: str, text_content: str) -> None:
        """Store parsed text in database."""
        # TODO: Implement database storage
        # 1. Connect to PostgreSQL
        # 2. Update documents table with parsed_text
        # 3. Handle connection errors
        pass

    def _update_document_status(self, document_id: str, status: str, metadata: dict[str, Any] | None = None) -> None:
        """Update document processing status."""
        # TODO: Implement status update
        # 1. Connect to PostgreSQL
        # 2. Update processing_status and processing_metadata
        # 3. Handle connection errors
        pass


def main() -> None:
    """Main entry point."""
    worker = ParserWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping parser worker")
        worker.stop()


if __name__ == "__main__":
    main()