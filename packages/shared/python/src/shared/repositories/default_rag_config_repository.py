"""Default RAG config repository interface."""

from abc import ABC, abstractmethod

from shared.models.default_rag_config import DefaultRagConfig


class DefaultRagConfigRepository(ABC):
    """Abstract repository for default RAG configurations."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> DefaultRagConfig | None:
        """Get default RAG config for a user."""
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
        """Create or update default RAG config for a user."""
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> bool:
        """Delete default RAG config for a user."""
        pass
