"""RAG config repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from shared.models.workspace import RagConfig


class RagConfigRepository(ABC):
    """Interface for RagConfig repository operations."""

    @abstractmethod
    def create_rag_config(
        self,
        workspace_id: int,
        embedding_model: str,
        retriever_type: str,
        chunk_size: int,
        chunk_overlap: int,
        top_k: int,
        rerank_enabled: bool = False,
        rerank_model: Optional[str] = None,
    ) -> RagConfig:
        """
        Create a new RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            embedding_model: The embedding model to use
            retriever_type: The retriever type ('vector', 'graph', 'hybrid')
            chunk_size: The chunk size for text splitting
            chunk_overlap: The chunk overlap for text splitting
            top_k: The number of top results to retrieve
            rerank_enabled: Whether reranking is enabled
            rerank_model: The reranking model (optional)

        Returns:
            The created RagConfig
        """
        pass

    @abstractmethod
    def get_rag_config(self, workspace_id: int) -> Optional[RagConfig]:
        """
        Get RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            RagConfig if found, None otherwise
        """
        pass

    @abstractmethod
    def update_rag_config(
        self,
        workspace_id: int,
        embedding_model: Optional[str] = None,
        retriever_type: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        top_k: Optional[int] = None,
        rerank_enabled: Optional[bool] = None,
        rerank_model: Optional[str] = None,
    ) -> Optional[RagConfig]:
        """
        Update RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            embedding_model: The embedding model to use
            retriever_type: The retriever type
            chunk_size: The chunk size
            chunk_overlap: The chunk overlap
            top_k: The number of top results
            rerank_enabled: Whether reranking is enabled
            rerank_model: The reranking model

        Returns:
            Updated RagConfig if successful, None otherwise
        """
        pass