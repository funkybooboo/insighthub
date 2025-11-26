"""Document chunker worker for splitting text into processable chunks."""

import json
import logging
from typing import Any, Dict, List
from uuid import uuid4

from shared.config import AppConfig
from shared.database.sql.postgres import PostgresConnection
from shared.documents.chunking.factory import create_chunker
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.worker import Worker

logger = logging.getLogger(__name__)


class ChunkerWorker(Worker):
    """
    Worker for chunking documents into smaller text segments.

    Consumes: document.parsed
    Produces: document.chunked
    """

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ):
        """Initialize the chunker worker."""
        super().__init__(consumer, publisher, config)

        # Initialize chunker
        chunk_strategy = getattr(config, "chunk_strategy", "sentence")
        chunk_size = config.chunk_size
        chunk_overlap = config.chunk_overlap

        self.chunker = create_chunker(chunk_strategy, chunk_size, chunk_overlap)
        if not self.chunker:
            raise ValueError(f"Invalid chunker strategy: {chunk_strategy}")

        # Initialize database connection
        self.db = PostgresConnection(db_url=config.database_url)
        self.db.connect()

    def process_message(self, message: Dict[str, Any]) -> None:
        """
        Process document.parsed event to create chunks.

        Args:
            message: Event data containing parsed document metadata
        """
        document_id = str(message.get("document_id", ""))
        workspace_id = str(message.get("workspace_id", ""))
        metadata = message.get("metadata", {})

        if not document_id or not workspace_id:
            logger.error("Missing required fields in message", extra=message)
            return

        logger.info(
            f"Chunking document {document_id}",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
            },
        )

        try:
            # Update status to chunking
            self._update_document_status(document_id, "chunking")

            # Retrieve parsed text
            parsed_text = self._get_parsed_text(document_id)
            if not parsed_text:
                raise ValueError("No parsed text found")

            # Chunk the document
            chunk_ids = self._chunk_document(document_id, workspace_id, parsed_text)

            # Update status to chunked
            self._update_document_status(
                document_id, "chunked", {"chunk_count": len(chunk_ids)}
            )

            # Publish chunked event
            self.publisher.publish_event(
                routing_key="document.chunked",
                event={
                    "event_type": "document.chunked",
                    "document_id": document_id,
                    "workspace_id": workspace_id,
                    "chunk_ids": chunk_ids,
                    "chunk_count": len(chunk_ids),
                    "metadata": metadata,
                },
            )

            logger.info(
                f"Successfully chunked document {document_id}",
                extra={"chunk_count": len(chunk_ids)},
            )

        except Exception as e:
            logger.error(
                f"Failed to chunk document {document_id}: {e}",
                exc_info=True,
            )
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _get_parsed_text(self, document_id: str) -> str:
        """Retrieve parsed text from database."""
        logger.info(f"Retrieving parsed text for document {document_id}")

        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    "SELECT parsed_text FROM documents WHERE id = %s",
                    (document_id,),
                )
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Document {document_id} not found")
                return row[0] or ""
        except Exception as e:
            raise Exception(f"Failed to retrieve parsed text: {e}")

    def _chunk_document(
        self, document_id: str, workspace_id: str, text: str
    ) -> List[str]:
        """Chunk document text and store chunks."""
        logger.info(f"Chunking text for document {document_id}")

        # Generate chunks
        chunks_result = self.chunker.chunk_text(text)
        if chunks_result.is_err():
            error = chunks_result.error  # type: ignore
            raise Exception(f"Failed to chunk text: {error}")

        chunks = chunks_result.unwrap()

        # Store chunks in database
        chunk_ids: List[str] = []
        for index, chunk_text in enumerate(chunks):
            chunk_id = str(uuid4())
            self._store_chunk(
                chunk_id=chunk_id,
                document_id=document_id,
                workspace_id=workspace_id,
                chunk_index=index,
                chunk_text=chunk_text,
            )
            chunk_ids.append(chunk_id)

        return chunk_ids

    def _store_chunk(
        self,
        chunk_id: str,
        document_id: str,
        workspace_id: str,
        chunk_index: int,
        chunk_text: str,
    ) -> None:
        """Store a chunk in the database."""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chunks (
                        chunk_id, document_id, workspace_id,
                        chunk_index, chunk_text, metadata,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """,
                    (
                        chunk_id,
                        document_id,
                        workspace_id,
                        chunk_index,
                        chunk_text,
                        json.dumps({"length": len(chunk_text)}),
                    ),
                )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to store chunk: {e}")

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


def create_chunker_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: AppConfig,
) -> ChunkerWorker:
    """Factory function to create chunker worker."""
    return ChunkerWorker(consumer, publisher, config)
