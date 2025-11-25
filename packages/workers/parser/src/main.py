"""
Parser Worker - Document text extraction.

Consumes: document.uploaded
Produces: document.parsed
"""

import io
import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from shared.config import config
from shared.database.sql.postgres import PostgresConnection
from shared.documents.parsing.factory import parser_factory
from shared.logger import create_logger
from shared.storage.s3_blob_storage import S3BlobStorage
from shared.worker.worker import Worker as BaseWorker

logger = create_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
MINIO_URL = config.s3_endpoint_url
MINIO_ACCESS_KEY = config.s3_access_key
MINIO_SECRET_KEY = config.s3_secret_key
MINIO_BUCKET_NAME = config.s3_bucket_name
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
        if not all([MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME]):
            raise ValueError("MinIO configuration is missing.")

        self.blob_storage = S3BlobStorage(
            endpoint=MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            bucket_name=MINIO_BUCKET_NAME,
            secure=False,  # Assuming non-secure for local dev, should be configurable
        )

    def parse_document(
        self, document_id: str, content_type: str, file_path: str
    ) -> str:
        """
        Parse document content based on content type.
        """
        logger.info(
            "Downloading document from blob storage",
            extra={"document_id": document_id, "file_path": file_path},
        )

        download_result = self.blob_storage.download_file(file_path)
        if download_result.is_err():
            err = download_result.unwrap_err()  # type: ignore
            logger.error("Failed to download file", extra={"error": str(err)})
            raise err

        file_bytes = download_result.unwrap()
        file_obj = io.BytesIO(file_bytes)

        filename = os.path.basename(file_path)

        logger.info(
            "Parsing document content",
            extra={"document_id": document_id, "filename": filename},
        )

        parse_result = parser_factory.parse_document(file_obj, filename)
        if parse_result.is_err():
            err = parse_result.unwrap_err()  # type: ignore
            logger.error("Failed to parse document", extra={"error": str(err)})
            raise err

        document = parse_result.unwrap()
        return document.content


class ParserWorker(BaseWorker):
    """Document parser worker."""

    def __init__(self) -> None:
        """Initialize the parser worker."""
        super().__init__(
            worker_name="parser",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.uploaded",
            consume_queue="parser.document.uploaded",
            prefetch_count=WORKER_CONCURRENCY,
        )

        self.parser = DocumentParser()
        self.db_connection = PostgresConnection(db_url=DATABASE_URL)
        self.db_connection.connect()

    def stop(self):
        self._consumer.stop()

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process document.uploaded event to extract text.
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
                "file_path": file_path,
            },
        )

        try:
            self._update_document_status(document_id, "parsing")

            text_content = self.parser.parse_document(
                document_id, content_type, file_path
            )
            text_length = len(text_content)

            self._store_parsed_text(document_id, text_content)

            self._update_document_status(
                document_id, "parsed", {"text_length": text_length}
            )

            parsed_event = DocumentParsedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                content_type=content_type,
                text_length=text_length,
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.parsed",
                event=asdict(parsed_event),
            )

            logger.info(
                "Successfully parsed document",
                extra={"document_id": document_id, "text_length": text_length},
            )

        except Exception as e:
            logger.error(
                "Failed to parse document",
                extra={"document_id": document_id, "error": str(e)},
            )
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _store_parsed_text(self, document_id: str, text_content: str) -> None:
        """Store parsed text in database."""
        logger.info(
            "Storing parsed text in database", extra={"document_id": document_id}
        )
        try:
            with self.db_connection.get_cursor() as cursor:
                cursor.execute(
                    "UPDATE documents SET parsed_text = %s, updated_at = NOW() WHERE id = %s",
                    (text_content, document_id),
                )
                if self.db_connection.connection:
                    self.db_connection.connection.commit()
        except Exception as e:
            logger.error(
                "Failed to store parsed text",
                extra={"document_id": document_id, "error": str(e)},
            )
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            raise

    def _update_document_status(
        self, document_id: str, status: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Update document processing status."""
        logger.info(
            "Updating document status",
            extra={"document_id": document_id, "status": status},
        )
        try:
            with self.db_connection.get_cursor() as cursor:
                query = """
                    UPDATE documents
                    SET processing_status = %s, processing_metadata = %s, updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(
                    query,
                    (status, json.dumps(metadata) if metadata else None, document_id),
                )
                if self.db_connection.connection:
                    self.db_connection.connection.commit()
        except Exception as e:
            logger.error(
                "Failed to update document status",
                extra={"document_id": document_id, "error": str(e)},
            )
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            raise


def main() -> None:
    """Main entry point."""
    worker = ParserWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping parser worker")
        worker.stop()
    except Exception as e:
        logger.error(f"Parser worker failed: {e}")
        worker.stop()


if __name__ == "__main__":
    main()
