"""Vector RAG configuration repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from shared.types.rag import VectorRagConfig


class VectorRagConfigRepository(ABC):
    """Interface for VectorRagConfig repository operations."""

    @abstractmethod
    def create_vector_rag_config(
        self,
        workspace_id: int,
        embedding_algorithm: str = "nomic-embed-text",
        chunking_algorithm: str = "sentence",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 8,
        rerank_enabled: bool = False,
        rerank_algorithm: Optional[str] = None,
    ) -> VectorRagConfig:
        """
        Create a new Vector RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            embedding_algorithm: The embedding algorithm to use
            chunking_algorithm: The chunking algorithm to use
            chunk_size: The chunk size for text splitting
            chunk_overlap: The chunk overlap for text splitting
            top_k: The number of top results to retrieve
            rerank_enabled: Whether reranking is enabled
            rerank_algorithm: The reranking algorithm (optional)

        Returns:
            The created VectorRagConfig
        """
        pass

    @abstractmethod
    def get_vector_rag_config(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """
        Get Vector RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            VectorRagConfig if found, None otherwise
        """
        pass

    @abstractmethod
    def update_vector_rag_config(
        self,
        workspace_id: int,
        embedding_algorithm: Optional[str] = None,
        chunking_algorithm: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        top_k: Optional[int] = None,
        rerank_enabled: Optional[bool] = None,
        rerank_algorithm: Optional[str] = None,
    ) -> Optional[VectorRagConfig]:
        """
        Update Vector RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            embedding_algorithm: The embedding algorithm to use
            chunking_algorithm: The chunking algorithm to use
            chunk_size: The chunk size
            chunk_overlap: The chunk overlap
            top_k: The number of top results
            rerank_enabled: Whether reranking is enabled
            rerank_algorithm: The reranking algorithm

        Returns:
            Updated VectorRagConfig if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_vector_rag_config(self, workspace_id: int) -> bool:
        """
        Delete Vector RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            True if deleted, False otherwise
        """
        pass