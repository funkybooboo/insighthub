"""
Chucker Worker - Document chunking for embeddings.

Consumes: document.parsed
Produces: document.chunked
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, List

from shared.config import config
from shared.database.sql.postgres import PostgresConnection
from shared.documents.chunking.factory import create_chunker
from shared.logger import create_logger
from shared.types.document import Document
from shared.worker.worker import Worker as BaseWorker

logger = create_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
WORKER_CONCURRENCY = config.worker_concurrency
CHUNK_SIZE = config.chunk_size
CHUNK_OVERLAP = config.chunk_overlap
CHUNK_STRATEGY = "sentence"


@dataclass
class DocumentChunkedEvent:
    """Event emitted when document is chunked."""

    document_id: str
    workspace_id: str
    chunk_ids: list[str]
    chunk_count: int
    metadata: dict[str, Any]


class ChuckerWorker(BaseWorker):
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

        self.chunker = create_chunker(CHUNK_STRATEGY, CHUNK_SIZE, CHUNK_OVERLAP)
        if not self.chunker:
            raise ValueError(f"Invalid chunker type: {CHUNK_STRATEGY}")

        self.db_connection = PostgresConnection(db_url=DATABASE_URL)
        self.db_connection.connect()

    def stop(self):
        self._consumer.stop()

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process document.parsed event to create chunks.
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Chunking document",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "chunk_size": CHUNK_SIZE,
                "strategy": CHUNK_STRATEGY,
            },
        )

        try:
            self._update_document_status(document_id, "chunking")

            text_content = self._get_parsed_text(document_id)
            if not text_content:
                raise ValueError(f"No parsed text found for document {document_id}")

            if not self.chunker:
                raise ValueError(f"Invalid chunker type: {CHUNK_STRATEGY}")
            doc = Document(
                id=document_id,
                workspace_id=workspace_id,
                title="",
                content=text_content,
                metadata={},
            )
            chunks = self.chunker.chunk(doc)

            chunk_ids = self._store_chunks(document_id, chunks)

            self._update_document_status(
                document_id, "chunked", {"chunk_count": len(chunk_ids)}
            )

            chunked_event = DocumentChunkedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                chunk_ids=chunk_ids,
                chunk_count=len(chunk_ids),
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.chunked",
                event=asdict(chunked_event),
            )

            logger.info(
                "Successfully chunked document",
                extra={"document_id": document_id, "chunk_count": len(chunk_ids)},
            )

        except Exception as e:
            logger.error(
                "Failed to chunk document",
                extra={"document_id": document_id, "error": str(e)},
            )
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _get_parsed_text(self, document_id: str) -> str | None:
        """Get parsed text from database."""
        logger.info(
            "Getting parsed text from database", extra={"document_id": document_id}
        )
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    "SELECT parsed_text FROM documents WHERE id = %s", (document_id,)
                )
                result = cursor.fetchone()
                return result["parsed_text"] if result else None
        except Exception as e:
            logger.error(
                "Failed to get parsed text",
                extra={"document_id": document_id, "error": str(e)},
            )
            raise

    def _store_chunks(self, document_id: str, chunks: List[Any]) -> list[str]:
        """Store text chunks in database and return chunk IDs."""
        logger.info(
            f"Storing {len(chunks)} chunks for document",
            extra={"document_id": document_id},
        )
        try:
            with self.db_connection.get_cursor() as cursor:
                chunk_data = [
                    (document_id, i, chunk.text) for i, chunk in enumerate(chunks)
                ]

                # Using execute_many for bulk insert
                from psycopg2.extras import execute_values

                query = "INSERT INTO document_chunks (document_id, chunk_index, chunk_text) VALUES %s RETURNING id"

                # execute_values returns the fetched results
                results = execute_values(cursor, query, chunk_data, fetch=True)

                self.db_connection.connection.commit()

                chunk_ids = [str(row[0]) for row in results]
                logger.info(
                    f"Successfully stored {len(chunk_ids)} chunks",
                    extra={"document_id": document_id},
                )
                return chunk_ids

        except Exception as e:
            logger.error(
                "Failed to store chunks",
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
                query = "UPDATE documents SET processing_status = %s, processing_metadata = %s, updated_at = NOW() WHERE id = %s"
                cursor.execute(
                    query,
                    (status, json.dumps(metadata) if metadata else None, document_id),
                )
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
    worker = ChuckerWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping chucker worker")
        worker.stop()
    except Exception as e:
        logger.error(f"Chucker worker failed: {e}")
        worker.stop()


if __name__ == "__main__":
    main()
