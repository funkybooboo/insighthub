"""Vector RAG implementation of remove document workflow."""

from typing import TYPE_CHECKING

from returns.result import Failure, Result, Success

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.remove_document.remove_document_workflow import (
    RemoveDocumentWorkflow,
    RemoveDocumentWorkflowError,
)
from src.infrastructure.vector_stores import QdrantVectorDatabase

if TYPE_CHECKING:
    from qdrant_client.http.models import Filter

logger = create_logger(__name__)

try:
    import qdrant_client.http.models as qdrant_models

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class VectorRagRemoveDocumentWorkflow(RemoveDocumentWorkflow):
    """
    Vector RAG implementation of document removal workflow.

    Pipeline:
    1. Query vector store for all chunks with matching document_id metadata
    2. Delete all matching chunks
    3. Return count of deleted chunks
    """

    def __init__(self, vector_database: QdrantVectorDatabase):
        """Initialize workflow with Qdrant vector database.

        Args:
            vector_database: Qdrant vector database for chunk storage
        """
        self.vector_database = vector_database

    def execute(
        self,
        document_id: str,
        workspace_id: str,
    ) -> Result[int, RemoveDocumentWorkflowError]:
        """Execute removal workflow for a document.

        Args:
            document_id: Unique document identifier
            workspace_id: Workspace identifier for filtering

        Returns:
            Result containing number of chunks removed, or error
        """
        try:
            logger.info(f"Starting document removal for document_id={document_id}")

            # Get count of chunks to delete using Qdrant scroll/filter
            # Note: We need to use the underlying client to query by metadata
            chunks_deleted = self._delete_chunks_by_metadata(document_id, workspace_id)

            logger.info(f"Removed {chunks_deleted} chunks for document {document_id}")

            return Success(chunks_deleted)

        except Exception as e:
            logger.error(f"Document removal failed: {e}", exc_info=True)
            return Failure(
                RemoveDocumentWorkflowError(
                    message=f"Failed to remove document: {str(e)}",
                    step="document_removal",
                )
            )

    def _delete_chunks_by_metadata(self, document_id: str, workspace_id: str) -> int:
        """Delete all chunks with matching document_id and workspace_id metadata.

        Args:
            document_id: Document identifier to match
            workspace_id: Workspace identifier to match

        Returns:
            Number of chunks deleted
        """
        try:
            filter_conditions = self._build_metadata_filter(document_id, workspace_id)
            collection_name = self.vector_database.collection_name
            client = self.vector_database._client

            deleted_count = self._scroll_and_delete(client, collection_name, filter_conditions)
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete chunks by metadata: {e}")
            raise Exception(f"Chunk deletion failed: {e}") from e

    def _build_metadata_filter(self, document_id: str, workspace_id: str) -> "Filter":
        """Build filter for document_id and workspace_id."""
        return qdrant_models.Filter(
            must=[
                qdrant_models.FieldCondition(
                    key="document_id",
                    match=qdrant_models.MatchValue(value=document_id),
                ),
                qdrant_models.FieldCondition(
                    key="workspace_id",
                    match=qdrant_models.MatchValue(value=workspace_id),
                ),
            ]
        )

    def _scroll_and_delete(self, client, collection_name: str, filter_conditions: "Filter") -> int:
        """Scroll through matching points and delete them in batches."""
        offset = None
        deleted_count = 0
        batch_size = 100

        while True:
            scroll_result = client.scroll(
                collection_name=collection_name,
                scroll_filter=filter_conditions,
                limit=batch_size,
                offset=offset,
                with_payload=False,
                with_vectors=False,
            )

            points, next_offset = scroll_result

            if not points:
                break

            deleted_count += self._delete_point_batch(client, collection_name, points)

            if next_offset is None:
                break

            offset = next_offset

        return deleted_count

    def _delete_point_batch(self, client, collection_name: str, points: list) -> int:
        """Delete a batch of points and return count deleted."""
        point_ids = [point.id for point in points]
        if not point_ids:
            return 0

        client.delete(
            collection_name=collection_name,
            points_selector=qdrant_models.PointIdsList(points=point_ids),
        )
        return len(point_ids)
