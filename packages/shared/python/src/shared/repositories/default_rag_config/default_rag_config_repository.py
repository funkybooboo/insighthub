"""Default RAG config repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from shared.models.default_rag_config import DefaultRagConfig


class DefaultRagConfigRepository(ABC):
    """Interface for DefaultRagConfig repository operations."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[DefaultRagConfig]:
        """
        Get default RAG config for a user.

        Args:
            user_id: User ID

        Returns:
            DefaultRagConfig if found, None if not found
        """
        pass

    @abstractmethod
    def upsert(
        self,
        user_id: int,
        embedding_model: str = "nomic-embed-text",
        embedding_dim: int | None = None,
        retriever_type: str = "vector",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 8,
        rerank_enabled: bool = False,
        rerank_model: str | None = None,
    ) -> DefaultRagConfig:
        """
        Create or update default RAG config for a user.

        Args:
            user_id: User ID
            **kwargs: Configuration fields to set

        Returns:
            Created or updated DefaultRagConfig
        """
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> bool:
        """
        Delete default RAG config for a user.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        pass
