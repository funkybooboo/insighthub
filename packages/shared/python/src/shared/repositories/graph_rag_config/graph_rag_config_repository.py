"""Graph RAG configuration repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from shared.types.rag import GraphRagConfig


class GraphRagConfigRepository(ABC):
    """Interface for GraphRagConfig repository operations."""

    @abstractmethod
    def create_graph_rag_config(
        self,
        workspace_id: int,
        entity_extraction_algorithm: str = "ollama",
        relationship_extraction_algorithm: str = "ollama",
        clustering_algorithm: str = "leiden",
        max_hops: int = 2,
        min_cluster_size: int = 5,
        max_cluster_size: int = 50,
    ) -> GraphRagConfig:
        """
        Create a new Graph RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            entity_extraction_algorithm: The entity extraction algorithm to use
            relationship_extraction_algorithm: The relationship extraction algorithm to use
            clustering_algorithm: The clustering algorithm to use
            max_hops: Maximum hops for graph traversal
            min_cluster_size: Minimum cluster size
            max_cluster_size: Maximum cluster size

        Returns:
            The created GraphRagConfig
        """
        pass

    @abstractmethod
    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """
        Get Graph RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            GraphRagConfig if found, None otherwise
        """
        pass

    @abstractmethod
    def update_graph_rag_config(
        self,
        workspace_id: int,
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
            entity_extraction_algorithm: The entity extraction algorithm to use
            relationship_extraction_algorithm: The relationship extraction algorithm to use
            clustering_algorithm: The clustering algorithm to use
            max_hops: Maximum hops for graph traversal
            min_cluster_size: Minimum cluster size
            max_cluster_size: Maximum cluster size

        Returns:
            Updated GraphRagConfig if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_graph_rag_config(self, workspace_id: int) -> bool:
        """
        Delete Graph RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            True if deleted, False otherwise
        """
        pass