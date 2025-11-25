"""Graph RAG configuration service."""

from typing import Optional

from shared.repositories.graph_rag_config.graph_rag_config_repository import GraphRagConfigRepository
from shared.repositories.workspace.workspace_repository import WorkspaceRepository
from shared.types.rag import GraphRagConfig


class GraphRagConfigService:
    """Service for Graph RAG configuration operations."""

    def __init__(self, repository: GraphRagConfigRepository, workspace_repository: WorkspaceRepository):
        """Initialize the service."""
        self.repository = repository
        self.workspace_repository = workspace_repository

    def _validate_workspace_access(self, workspace_id: int, user_id: int) -> bool:
        """Validate that user has access to the workspace."""
        workspace = self.workspace_repository.get_by_id(workspace_id)
        return workspace is not None and workspace.user_id == user_id

    def get_graph_rag_config(self, workspace_id: int, user_id: int) -> Optional[GraphRagConfig]:
        """
        Get Graph RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID

        Returns:
            GraphRagConfig if found, None otherwise
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            return None
        return self.repository.get_graph_rag_config(workspace_id)

    def create_graph_rag_config(
        self,
        workspace_id: int,
        user_id: int,
        entity_extraction_algorithm: str = "ollama",
        relationship_extraction_algorithm: str = "ollama",
        clustering_algorithm: str = "leiden",
        max_hops: int = 2,
        min_cluster_size: int = 5,
        max_cluster_size: int = 50,
    ) -> GraphRagConfig:
        """
        Create Graph RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)
            entity_extraction_algorithm: The entity extraction algorithm to use
            relationship_extraction_algorithm: The relationship extraction algorithm to use
            clustering_algorithm: The clustering algorithm to use
            max_hops: Maximum hops for graph traversal
            min_cluster_size: Minimum cluster size
            max_cluster_size: Maximum cluster size

        Returns:
            Created GraphRagConfig

        Raises:
            ValueError: If validation fails
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            raise ValueError("User does not have access to this workspace")

        self._validate_graph_config(
            entity_extraction_algorithm=entity_extraction_algorithm,
            relationship_extraction_algorithm=relationship_extraction_algorithm,
            clustering_algorithm=clustering_algorithm,
            max_hops=max_hops,
            min_cluster_size=min_cluster_size,
            max_cluster_size=max_cluster_size,
        )

        # Check if config already exists
        existing = self.repository.get_graph_rag_config(workspace_id)
        if existing:
            raise ValueError("Graph RAG configuration already exists for this workspace")

        return self.repository.create_graph_rag_config(
            workspace_id=workspace_id,
            entity_extraction_algorithm=entity_extraction_algorithm,
            relationship_extraction_algorithm=relationship_extraction_algorithm,
            clustering_algorithm=clustering_algorithm,
            max_hops=max_hops,
            min_cluster_size=min_cluster_size,
            max_cluster_size=max_cluster_size,
        )

    def update_graph_rag_config(
        self,
        workspace_id: int,
        user_id: int,
        entity_extraction_algorithm: Optional[str] = None,
        relationship_extraction_algorithm: Optional[str] = None,
        clustering_algorithm: Optional[str] = None,
        max_hops: Optional[int] = None,
        min_cluster_size: Optional[int] = None,
        max_cluster_size: Optional[int] = None,
    ) -> Optional[GraphRagConfig]:
        """
        Update Graph RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)
            entity_extraction_algorithm: The entity extraction algorithm to use
            relationship_extraction_algorithm: The relationship extraction algorithm to use
            clustering_algorithm: The clustering algorithm to use
            max_hops: Maximum hops for graph traversal
            min_cluster_size: Minimum cluster size
            max_cluster_size: Maximum cluster size

        Returns:
            Updated GraphRagConfig if successful, None otherwise

        Raises:
            ValueError: If validation fails
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            return None

        if any([
            entity_extraction_algorithm, relationship_extraction_algorithm,
            clustering_algorithm, max_hops, min_cluster_size, max_cluster_size
        ]):
            # Get current config for validation
            current = self.repository.get_graph_rag_config(workspace_id)
            if current:
                self._validate_graph_config(
                    entity_extraction_algorithm=entity_extraction_algorithm or current.entity_extraction_algorithm,
                    relationship_extraction_algorithm=relationship_extraction_algorithm or current.relationship_extraction_algorithm,
                    clustering_algorithm=clustering_algorithm or current.clustering_algorithm,
                    max_hops=max_hops if max_hops is not None else current.max_hops,
                    min_cluster_size=min_cluster_size if min_cluster_size is not None else current.min_cluster_size,
                    max_cluster_size=max_cluster_size if max_cluster_size is not None else current.max_cluster_size,
                )

        return self.repository.update_graph_rag_config(
            workspace_id=workspace_id,
            entity_extraction_algorithm=entity_extraction_algorithm,
            relationship_extraction_algorithm=relationship_extraction_algorithm,
            clustering_algorithm=clustering_algorithm,
            max_hops=max_hops,
            min_cluster_size=min_cluster_size,
            max_cluster_size=max_cluster_size,
        )

    def delete_graph_rag_config(self, workspace_id: int, user_id: int) -> bool:
        """
        Delete Graph RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)

        Returns:
            True if deleted, False otherwise
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            return False
        return self.repository.delete_graph_rag_config(workspace_id)

    def _validate_graph_config(
        self,
        entity_extraction_algorithm: str,
        relationship_extraction_algorithm: str,
        clustering_algorithm: str,
        max_hops: int,
        min_cluster_size: int,
        max_cluster_size: int,
    ) -> None:
        """
        Validate Graph RAG configuration data.

        Args:
            entity_extraction_algorithm: The entity extraction algorithm
            relationship_extraction_algorithm: The relationship extraction algorithm
            clustering_algorithm: The clustering algorithm
            max_hops: Maximum hops for graph traversal
            min_cluster_size: Minimum cluster size
            max_cluster_size: Maximum cluster size

        Raises:
            ValueError: If validation fails
        """
        # Validate entity extraction algorithm
        valid_entity_algorithms = ["ollama", "spacy"]
        if entity_extraction_algorithm not in valid_entity_algorithms:
            raise ValueError(f"entity_extraction_algorithm must be one of: {', '.join(valid_entity_algorithms)}")

        # Validate relationship extraction algorithm
        valid_relationship_algorithms = ["ollama", "rule-based"]
        if relationship_extraction_algorithm not in valid_relationship_algorithms:
            raise ValueError(f"relationship_extraction_algorithm must be one of: {', '.join(valid_relationship_algorithms)}")

        # Validate clustering algorithm
        valid_clustering_algorithms = ["leiden", "louvain"]
        if clustering_algorithm not in valid_clustering_algorithms:
            raise ValueError(f"clustering_algorithm must be one of: {', '.join(valid_clustering_algorithms)}")

        # Validate max_hops
        if not (1 <= max_hops <= 10):
            raise ValueError("max_hops must be between 1 and 10")

        # Validate cluster sizes
        if min_cluster_size < 1:
            raise ValueError("min_cluster_size must be at least 1")
        if max_cluster_size < min_cluster_size:
            raise ValueError("max_cluster_size must be greater than or equal to min_cluster_size")