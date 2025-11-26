"""Document parser worker for extracting text from various file formats."""

import io
import json
import logging
import os
from typing import Any, Dict

from shared.config import AppConfig
from shared.database.sql.postgres import PostgresConnection
from shared.documents.parsing.factory import parser_factory
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.storage.s3_blob_storage import S3BlobStorage
from shared.worker import Worker

logger = logging.getLogger(__name__)


class ParserWorker(Worker):
    """
    Worker for parsing documents and extracting text content.

    Consumes: document.uploaded
    Produces: document.parsed
    """

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ):
        """Initialize the parser worker."""
        super().__init__(consumer, publisher, config)

        # Initialize blob storage
        if not all(
            [
                config.s3_endpoint_url,
                config.s3_access_key,
                config.s3_secret_key,
                config.s3_bucket_name,
            ]
        ):
            raise ValueError("S3/MinIO configuration is incomplete")

        self.blob_storage = S3BlobStorage(
            endpoint=config.s3_endpoint_url,
            access_key=config.s3_access_key,
            secret_key=config.s3_secret_key,
            bucket_name=config.s3_bucket_name,
            secure=False,
        )

        # Initialize database connection
        self.db = PostgresConnection(db_url=config.database_url)
        self.db.connect()

    def process_message(self, message: Dict[str, Any]) -> None:
        """
        Process document.uploaded event to extract text.

        Args:
            message: Event data containing document metadata
        """
        document_id = str(message.get("document_id", ""))
        workspace_id = str(message.get("workspace_id", ""))
        content_type = str(message.get("content_type", "text/plain"))
        file_path = str(message.get("file_path", ""))
        metadata = message.get("metadata", {})

        if not document_id or not workspace_id or not file_path:
            logger.error("Missing required fields in message", extra=message)
            return

        logger.info(
            f"Parsing document {document_id}",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "file_path": file_path,
            },
        )

        try:
            # Update status to parsing
            self._update_document_status(document_id, "parsing")

            # Download and parse document
            text_content = self._parse_document(document_id, content_type, file_path)
            text_length = len(text_content)

            # Store parsed text
            self._store_parsed_text(document_id, text_content)

            # Update status to parsed
            self._update_document_status(
                document_id, "parsed", {"text_length": text_length}
            )

            # Publish parsed event
            self.publisher.publish_event(
                routing_key="document.parsed",
                event={
                    "event_type": "document.parsed",
                    "document_id": document_id,
                    "workspace_id": workspace_id,
                    "content_type": content_type,
                    "text_length": text_length,
                    "metadata": metadata,
                },
            )

            logger.info(
                f"Successfully parsed document {document_id}",
                extra={"text_length": text_length},
            )

        except Exception as e:
            logger.error(
                f"Failed to parse document {document_id}: {e}",
                exc_info=True,
            )
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _parse_document(
        self, document_id: str, content_type: str, file_path: str
    ) -> str:
        """Download and parse document content."""
        logger.info(f"Downloading document from blob storage: {file_path}")

        download_result = self.blob_storage.download_file(file_path)
        if download_result.is_err():
            error = download_result.error  # type: ignore
            raise Exception(f"Failed to download file: {error}")

        file_bytes = download_result.unwrap()
        file_obj = io.BytesIO(file_bytes)
        filename = os.path.basename(file_path)

        logger.info(f"Parsing document content: {filename}")

        parse_result = parser_factory.parse_document(file_obj, filename)
        if parse_result.is_err():
            error = parse_result.error  # type: ignore
            raise Exception(f"Failed to parse document: {error}")

        document = parse_result.unwrap()
        return document.content

    def _store_parsed_text(self, document_id: str, text_content: str) -> None:
        """Store parsed text in database."""
        logger.info(f"Storing parsed text for document {document_id}")

        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE documents
                    SET parsed_text = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (text_content, document_id),
                )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to store parsed text: {e}")

    def _update_document_status(
        self, document_id: str, status: str, metadata: Dict[str, Any] | None = None
    ) -> None:
        """Update document processing status."""
        logger.info(f"Updating document {document_id} status to {status}")

        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE documents
                    SET processing_status = %s,
                        processing_metadata = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (status, json.dumps(metadata) if metadata else None, document_id),
                )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to update document status: {e}")


def create_parser_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: AppConfig,
) -> ParserWorker:
    """Factory function to create parser worker."""
    return ParserWorker(consumer, publisher, config)
