"""Vector RAG implementation of create RAG resources workflow."""

from typing import TYPE_CHECKING

from returns.result import Failure, Result, Success

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.create_resources.create_rag_resources_workflow import (
    CreateRagResourcesWorkflow,
    CreateRagResourcesWorkflowError,
)

if TYPE_CHECKING:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance

logger = create_logger(__name__)

try:
    import qdrant_client
    import qdrant_client.http.models as qdrant_models

    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class VectorRagCreateRagResourcesWorkflow(CreateRagResourcesWorkflow):
    """
    Vector RAG implementation of workspace provisioning workflow.

    Pipeline:
    1. Create Qdrant collection for the workspace
    2. Configure vector dimensions and distance metric
    3. Set up any required indexes
    4. Return success status
    """

    def __init__(self, qdrant_url: str, vector_size: int = 768, distance: str = "cosine"):
        """Initialize workflow with Qdrant connection parameters.

        Args:
            qdrant_url: Qdrant server URL
            vector_size: Dimension of vectors to store (default: 768 for nomic-embed-text)
            distance: Distance metric to use (cosine, euclidean, dot)
        """
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not installed. Please run: pip install qdrant-client")

        self.qdrant_url = qdrant_url
        self.vector_size = vector_size

        # Map distance string to Qdrant Distance enum
        distance_map = {
            "cosine": qdrant_models.Distance.COSINE,
            "euclidean": qdrant_models.Distance.EUCLID,
            "dot": qdrant_models.Distance.DOT,
        }
        self.distance = distance_map.get(distance.lower(), qdrant_models.Distance.COSINE)

    def execute(
        self,
        workspace_id: str,
        config: dict[str, str | int | float | bool] | None = None,
    ) -> Result[bool, CreateRagResourcesWorkflowError]:
        """Execute provisioning workflow for a workspace.

        Args:
            workspace_id: Unique workspace identifier
            config: Optional configuration parameters (vector_size, distance, etc.)

        Returns:
            Result containing success status (True), or error
        """
        try:
            logger.info(f"Starting workspace provisioning for workspace_id={workspace_id}")

            # Override defaults with config if provided
            vector_size = self.vector_size
            distance = self.distance

            if config:
                if "vector_size" in config:
                    vector_size = int(config["vector_size"])
                if "distance" in config:
                    distance_str = str(config["distance"])
                    distance_map = {
                        "cosine": Distance.COSINE,
                        "euclidean": Distance.EUCLID,
                        "dot": Distance.DOT,
                    }
                    distance = distance_map.get(distance_str.lower(), Distance.COSINE)

            # Create Qdrant collection
            collection_name = f"workspace_{workspace_id}"
            self._create_qdrant_collection(collection_name, vector_size, distance)

            logger.info(f"Workspace {workspace_id} provisioned successfully")

            return Success(True)

        except Exception as e:
            logger.error(f"Workspace provisioning failed: {e}", exc_info=True)
            return Failure(
                CreateRagResourcesWorkflowError(
                    message=f"Failed to provision workspace: {str(e)}",
                    step="workspace_provisioning",
                )
            )

    def _create_qdrant_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: "Distance",
    ) -> None:
        """Create Qdrant collection with specified parameters.

        Args:
            collection_name: Name of the collection to create
            vector_size: Dimension of vectors
            distance: Distance metric

        Raises:
            Exception: If collection creation fails
        """
        try:
            # Initialize Qdrant client
            client: QdrantClient = qdrant_client.QdrantClient(url=self.qdrant_url)

            # Check if collection already exists
            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]

            if collection_name in collection_names:
                logger.info(f"Collection {collection_name} already exists, skipping creation")
                return

            # Create collection
            client.create_collection(
                collection_name=collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=distance,
                ),
            )

            logger.info(f"Created Qdrant collection: {collection_name}")

        except Exception as e:
            raise Exception(f"Failed to create Qdrant collection: {e}") from e
