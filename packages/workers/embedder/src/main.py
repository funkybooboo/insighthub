"""
Embedder Worker - Generate embeddings from text chunks.

Consumes: document.chunked
Produces: document.embedded
"""

from dataclasses import asdict, dataclass
from typing import Any, List
import json

from shared.config import config
from shared.worker.worker import Worker as BaseWorker
from shared.logger import get_logger
from shared.database.sql.postgres import PostgresConnection
from shared.documents.embedding.factory import create_embedding_encoder

logger = get_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
WORKER_CONCURRENCY = config.worker_concurrency
EMBEDDING_MODEL = config.ollama_embedding_model
OLLAMA_BASE_URL = config.ollama_base_url
BATCH_SIZE = config.batch_size


@dataclass
class DocumentEmbeddedEvent:
    """Event emitted when document chunks are embedded."""

    document_id: str
    workspace_id: str
    chunk_ids: list[str]
    embedding_count: int
    metadata: dict[str, Any]


class EmbedderWorker(BaseWorker):
    """Document embedder worker."""

    def __init__(self) -> None:
        """Initialize the embedder worker."""
        super().__init__(
            worker_name="embedder",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.chunked",
            consume_queue="embedder.document.chunked",
            prefetch_count=WORKER_CONCURRENCY,
        )

        self.embedding_encoder = create_embedding_encoder(
            encoder_type="ollama",
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        if not self.embedding_encoder:
            raise ValueError("Failed to create embedding encoder.")

        self.db_connection = PostgresConnection(db_url=DATABASE_URL)
        self.db_connection.connect()

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process document.chunked event to generate embeddings.
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        chunk_ids = list(event_data.get("chunk_ids", []))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Embedding document chunks",
            extra={"document_id": document_id, "workspace_id": workspace_id, "chunk_count": len(chunk_ids)}
        )

        try:
            self._update_document_status(document_id, "embedding")

            chunk_texts = self._get_chunk_texts(chunk_ids)
            if not chunk_texts:
                raise ValueError(f"No chunk texts found for document {document_id}")

            embeddings_result = self.embedding_encoder.encode(chunk_texts)
            if embeddings_result.is_err():
                raise embeddings_result.unwrap_err()
            
            embeddings = embeddings_result.unwrap()

            self._store_embeddings(chunk_ids, embeddings)

            self._update_document_status(document_id, "embedded", {
                "embedding_count": len(embeddings),
                "embedding_dimension": self.embedding_encoder.get_dimension()
            })

            embedded_event = DocumentEmbeddedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                chunk_ids=chunk_ids,
                embedding_count=len(embeddings),
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.embedded",
                event=asdict(embedded_event),
            )

            logger.info(
                "Successfully embedded document",
                extra={"document_id": document_id, "embedding_count": len(embeddings)}
            )

        except Exception as e:
            logger.error("Failed to embed document", extra={"document_id": document_id, "error": str(e)})
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _get_chunk_texts(self, chunk_ids: list[str]) -> list[str]:
        """Get chunk texts from database."""
        logger.info(f"Getting {len(chunk_ids)} chunk texts from database", extra={"chunk_ids": chunk_ids})
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute("SELECT id, chunk_text FROM document_chunks WHERE id = ANY(%s)", (chunk_ids,))
                results = cursor.fetchall()
                
                # Sort the results to match the order of chunk_ids
                id_to_text_map = {str(row['id']): row['chunk_text'] for row in results}
                return [id_to_text_map[chunk_id] for chunk_id in chunk_ids if chunk_id in id_to_text_map]
        except Exception as e:
            logger.error("Failed to get chunk texts", extra={"error": str(e)})
            raise

    def _store_embeddings(self, chunk_ids: list[str], embeddings: list[list[float]]) -> None:
        """Store embeddings in database."""
        logger.info(f"Storing {len(embeddings)} embeddings in database")
        try:
            with self.db_connection.get_cursor() as cursor:
                from psycopg2.extras import execute_values
                
                update_data = [
                    (chunk_id, json.dumps(embedding))
                    for chunk_id, embedding in zip(chunk_ids, embeddings)
                ]
                
                query = "UPDATE document_chunks SET embedding = %s WHERE id = %s"
                
                # psycopg2 execute_values doesn't work well with UPDATE from values.
                # A simple loop is fine for now, or a more complex UPDATE FROM VALUES statement.
                # For simplicity and since the number of chunks per document is not huge, a loop is acceptable.
                for chunk_id, embedding in zip(chunk_ids, embeddings):
                    cursor.execute("UPDATE document_chunks SET embedding = %s WHERE id = %s", (json.dumps(embedding), chunk_id))
                
                self.db_connection.connection.commit()
                logger.info(f"Successfully stored {len(embeddings)} embeddings")

        except Exception as e:
            logger.error("Failed to store embeddings", extra={"error": str(e)})
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            raise

    def _update_document_status(self, document_id: str, status: str, metadata: dict[str, Any] | None = None) -> None:
        """Update document processing status."""
        logger.info("Updating document status", extra={"document_id": document_id, "status": status})
        try:
            with self.db_connection.get_cursor() as cursor:
                query = "UPDATE documents SET processing_status = %s, processing_metadata = %s, updated_at = NOW() WHERE id = %s"
                cursor.execute(query, (status, json.dumps(metadata) if metadata else None, document_id))
                self.db_connection.connection.commit()
        except Exception as e:
            logger.error("Failed to update document status", extra={"document_id": document_id, "error": str(e)})
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            raise

def main() -> None:
    """Main entry point."""
    worker = EmbedderWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping embedder worker")
        worker.stop()
    except Exception as e:
        logger.error(f"Embedder worker failed: {e}")
        worker.stop()

if __name__ == "__main__":
    main()
