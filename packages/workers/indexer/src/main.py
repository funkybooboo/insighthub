"""
Indexer Worker - Vector database indexing.

Consumes: document.embedded
Produces: document.indexed
"""

from dataclasses import asdict, dataclass
from typing import Any, List
import json
import uuid

from shared.config import config
from shared.worker.worker import Worker as BaseWorker
from shared.logger import get_logger
from shared.database.sql.postgres import PostgresConnection
from qdrant_client import QdrantClient, models

logger = get_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
QDRANT_URL = f"http://{config.qdrant_host}:{config.qdrant_port}"
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
            consume_routing_key="document.embedded",
            consume_queue="indexer.document.embedded",
            prefetch_count=WORKER_CONCURRENCY,
        )

        self.db_connection = PostgresConnection(db_url=DATABASE_URL)
        self.db_connection.connect()
        self.qdrant_client = QdrantClient(url=QDRANT_URL)

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process document.embedded event to index vectors.
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        chunk_ids = list(event_data.get("chunk_ids", []))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Indexing vectors",
            extra={"document_id": document_id, "workspace_id": workspace_id, "vector_count": len(chunk_ids)}
        )

        try:
            collection_name = self._get_workspace_collection(workspace_id)
            if not collection_name:
                raise ValueError(f"No collection name found for workspace {workspace_id}")

            self._update_document_status(document_id, "indexing")

            chunks = self._get_chunks_and_embeddings(chunk_ids)

            points = [
                models.PointStruct(
                    id=str(chunk["id"]),
                    vector=chunk["embedding"],
                    payload={
                        "document_id": document_id,
                        "chunk_text": chunk["chunk_text"],
                        "chunk_index": chunk["chunk_index"],
                    }
                ) for chunk in chunks if chunk.get("embedding")
            ]

            if not points:
                logger.warning("No embeddings to index", extra={"document_id": document_id})
                self._update_document_status(document_id, "failed", {"error": "No embeddings found to index"})
                return

            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True,
            )

            self._update_document_status(document_id, "ready", {
                "vector_count": len(points),
                "collection_name": collection_name
            })

            indexed_event = DocumentIndexedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                vector_count=len(points),
                collection_name=collection_name,
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.indexed",
                event=asdict(indexed_event),
            )

            logger.info(
                "Successfully indexed document",
                extra={"document_id": document_id, "vector_count": len(points), "collection_name": collection_name}
            )

        except Exception as e:
            logger.error("Failed to index document", extra={"document_id": document_id, "error": str(e)})
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _get_workspace_collection(self, workspace_id: str) -> str | None:
        """Get the Qdrant collection name for the workspace."""
        logger.info("Getting workspace collection", extra={"workspace_id": workspace_id})
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute("SELECT rag_collection FROM workspaces WHERE id = %s", (workspace_id,))
                result = cursor.fetchone()
                return result["rag_collection"] if result else None
        except Exception as e:
            logger.error("Failed to get workspace collection", extra={"workspace_id": workspace_id, "error": str(e)})
            raise
    
    def _get_chunks_and_embeddings(self, chunk_ids: List[str]) -> List[dict]:
        """Get chunks and their embeddings from the database."""
        logger.info(f"Getting {len(chunk_ids)} chunks and embeddings from database", extra={"chunk_ids": chunk_ids})
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                query = "SELECT id, chunk_text, chunk_index, embedding FROM document_chunks WHERE id = ANY(%s)"
                cursor.execute(query, (chunk_ids,))
                results = cursor.fetchall()
                # The embedding is stored as a JSON string, so we need to parse it.
                for r in results:
                    if isinstance(r['embedding'], str):
                        r['embedding'] = json.loads(r['embedding'])
                return results
        except Exception as e:
            logger.error("Failed to get chunks and embeddings", extra={"error": str(e)})
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
    worker = IndexerWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping indexer worker")
        worker.stop()
    except Exception as e:
        logger.error(f"Indexer worker failed: {e}")
        worker.stop()


if __name__ == "__main__":
    main()
