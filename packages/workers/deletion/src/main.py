"""
Deletion Worker - Workspace and document cleanup.

Consumes: workspace.deletion_requested, document.deleted
Produces: workspace.deletion_status
"""

from dataclasses import asdict, dataclass
from typing import Any, List
import json

from shared.config import config
from shared.worker.worker import Worker as BaseWorker
from shared.logger import get_logger
from shared.database.sql.postgres import PostgresConnection
from shared.storage.s3_blob_storage import S3BlobStorage
from qdrant_client import QdrantClient

logger = get_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
MINIO_URL = config.s3_endpoint_url
MINIO_ACCESS_KEY = config.s3_access_key
MINIO_SECRET_KEY = config.s3_secret_key
MINIO_BUCKET_NAME = config.s3_bucket_name
QDRANT_URL = f"http://{config.qdrant_host}:{config.qdrant_port}"
WORKER_CONCURRENCY = config.worker_concurrency


@dataclass
class WorkspaceDeletionStatusEvent:
    workspace_id: str
    status: str
    message: str

class DeletionWorker(BaseWorker):
    """Deletion worker for cleaning up workspaces and documents."""

    def __init__(self) -> None:
        """Initialize the deletion worker."""
        super().__init__(
            worker_name="deletion",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="#", # Listen to all keys under the exchange
            consume_queue="deletion_queue",
            prefetch_count=WORKER_CONCURRENCY,
        )
        self.db_connection = PostgresConnection(db_url=DATABASE_URL)
        self.db_connection.connect()
        self.qdrant_client = QdrantClient(url=QDRANT_URL)
        self.blob_storage = S3BlobStorage(
            endpoint=MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            bucket_name=MINIO_BUCKET_NAME,
            secure=False,
        )

    def on_message(self, ch, method, properties, body):
        routing_key = method.routing_key
        event_data = json.loads(body)

        try:
            if routing_key == "workspace.deletion_requested":
                self._handle_workspace_deletion(event_data)
            elif routing_key == "document.deleted":
                self._handle_document_deletion(event_data)
            else:
                logger.warning(f"Unknown routing key for deletion worker: {routing_key}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Failed to process deletion message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _handle_workspace_deletion(self, event_data: dict[str, Any]) -> None:
        workspace_id = str(event_data.get("workspace_id"))
        logger.info("Starting workspace deletion", extra={"workspace_id": workspace_id})

        try:
            self._publish_deletion_status(workspace_id, "deleting", "Starting workspace deletion")

            collection_name = self._get_workspace_collection(workspace_id)
            if collection_name:
                self.qdrant_client.delete_collection(collection_name)
                logger.info("Deleted Qdrant collection", extra={"collection_name": collection_name})

            file_paths = self._get_workspace_file_paths(workspace_id)
            for file_path in file_paths:
                self.blob_storage.delete_file(file_path)
                logger.info("Deleted file from blob storage", extra={"file_path": file_path})

            with self.db_connection.get_cursor() as cursor:
                cursor.execute("DELETE FROM workspaces WHERE id = %s", (workspace_id,))
                self.db_connection.connection.commit()
            logger.info("Deleted workspace record from database", extra={"workspace_id": workspace_id})

            self._publish_deletion_status(workspace_id, "completed", "Workspace deleted successfully")
            logger.info("Workspace deletion completed", extra={"workspace_id": workspace_id})

        except Exception as e:
            logger.error("Workspace deletion failed", extra={"workspace_id": workspace_id, "error": str(e)})
            self._publish_deletion_status(workspace_id, "failed", f"Workspace deletion failed: {e}")
            raise

    def _handle_document_deletion(self, event_data: dict[str, Any]) -> None:
        document_id = str(event_data.get("document_id"))
        file_path = str(event_data.get("file_path"))
        workspace_id = str(event_data.get("workspace_id"))
        logger.info("Deleting document", extra={"document_id": document_id})

        try:
            collection_name = self._get_workspace_collection(workspace_id)
            if not collection_name:
                raise ValueError(f"Could not find collection for workspace {workspace_id}")

            chunk_ids = self._get_document_chunk_ids(document_id)
            if chunk_ids:
                self.qdrant_client.delete_points(collection_name=collection_name, points_selector=chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} points from Qdrant", extra={"document_id": document_id})

            if file_path:
                self.blob_storage.delete_file(file_path)
                logger.info("Deleted file from blob storage", extra={"file_path": file_path})

            logger.info("Document deletion completed", extra={"document_id": document_id})

        except Exception as e:
            logger.error("Document deletion failed", extra={"document_id": document_id, "error": str(e)})
            raise

    def _publish_deletion_status(self, workspace_id: str, status: str, message: str) -> None:
        event = WorkspaceDeletionStatusEvent(workspace_id=workspace_id, status=status, message=message)
        self.publish_event(routing_key="workspace.deletion_status", event=asdict(event))

    def _get_workspace_collection(self, workspace_id: str) -> str | None:
        with self.db_connection.get_cursor(as_dict=True) as cursor:
            cursor.execute("SELECT rag_collection FROM workspaces WHERE id = %s", (workspace_id,))
            result = cursor.fetchone()
            return result["rag_collection"] if result else None

    def _get_workspace_file_paths(self, workspace_id: str) -> List[str]:
        with self.db_connection.get_cursor(as_dict=True) as cursor:
            cursor.execute("SELECT file_path FROM documents WHERE workspace_id = %s", (workspace_id,))
            return [row["file_path"] for row in cursor.fetchall()]

    def _get_document_chunk_ids(self, document_id: str) -> List[str]:
        with self.db_connection.get_cursor(as_dict=True) as cursor:
            cursor.execute("SELECT id FROM document_chunks WHERE document_id = %s", (document_id,))
            return [str(row["id"]) for row in cursor.fetchall()]

def main() -> None:
    worker = DeletionWorker()
    worker.start()

if __name__ == "__main__":
    main()
