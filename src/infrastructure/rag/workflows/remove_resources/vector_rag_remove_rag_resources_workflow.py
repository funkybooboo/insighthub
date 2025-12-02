"""Vector RAG implementation of remove RAG resources workflow."""

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.remove_resources.remove_rag_resources_workflow import (
    RemoveRagResourcesWorkflow,
    RemoveRagResourcesWorkflowError,
)
from src.infrastructure.types.result import Err, Ok, Result

logger = create_logger(__name__)

try:
    from qdrant_client import QdrantClient

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None


class VectorRagRemoveRagResourcesWorkflow(RemoveRagResourcesWorkflow):
    """
    Vector RAG implementation of workspace resource removal workflow.

    Pipeline:
    1. Connect to Qdrant
    2. Delete workspace collection
    3. Return success status
    """

    def __init__(self, qdrant_url: str):
        """Initialize workflow with Qdrant connection parameters.

        Args:
            qdrant_url: Qdrant server URL
        """
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not installed. Please run: pip install qdrant-client")

        self.qdrant_url = qdrant_url

    def execute(
        self,
        workspace_id: str,
    ) -> Result[bool, RemoveRagResourcesWorkflowError]:
        """Execute resource removal workflow for a workspace.

        Args:
            workspace_id: Unique workspace identifier

        Returns:
            Result containing success status (True), or error
        """
        try:
            logger.info(f"Starting RAG resource removal for workspace_id={workspace_id}")

            # Delete Qdrant collection
            collection_name = f"workspace_{workspace_id}"
            self._delete_qdrant_collection(collection_name)

            logger.info(f"Workspace {workspace_id} RAG resources removed successfully")

            return Ok(True)

        except Exception as e:
            logger.error(f"Workspace resource removal failed: {e}", exc_info=True)
            return Err(
                RemoveRagResourcesWorkflowError(
                    message=f"Failed to remove workspace resources: {str(e)}",
                    step="workspace_resource_removal",
                )
            )

    def _delete_qdrant_collection(self, collection_name: str) -> None:
        """Delete Qdrant collection.

        Args:
            collection_name: Name of the collection to delete

        Raises:
            Exception: If collection deletion fails
        """
        try:
            # Initialize Qdrant client
            client = QdrantClient(url=self.qdrant_url)

            # Check if collection exists before deleting
            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]

            if collection_name in collection_names:
                client.delete_collection(collection_name=collection_name)
                logger.info(f"Deleted Qdrant collection: {collection_name}")
            else:
                logger.info(f"Collection {collection_name} does not exist, skipping deletion")

        except Exception as e:
            logger.warning(f"Failed to delete Qdrant collection: {e}")
            # Don't raise exception - workspace deletion should continue
