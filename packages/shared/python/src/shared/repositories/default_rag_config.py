"""Repository for managing user default RAG configurations."""

from shared.models import DefaultRagConfig
from sqlalchemy.orm import Session


class DefaultRagConfigRepository:
    """Repository for default RAG config CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize the repository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(
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
        Create a new default RAG configuration for a user.

        Args:
            user_id: User ID
            embedding_model: Embedding model name
            embedding_dim: Optional embedding dimension
            retriever_type: Retriever type (vector, graph, hybrid)
            chunk_size: Chunk size for text splitting
            chunk_overlap: Overlap between chunks
            top_k: Number of results to retrieve
            rerank_enabled: Whether to enable reranking
            rerank_model: Optional rerank model name

        Returns:
            Created DefaultRagConfig instance
        """
        config = DefaultRagConfig(
            user_id=user_id,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
            retriever_type=retriever_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
            rerank_enabled=rerank_enabled,
            rerank_model=rerank_model,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def get_by_user_id(self, user_id: int) -> DefaultRagConfig | None:
        """
        Get default RAG configuration for a user.

        Args:
            user_id: User ID

        Returns:
            DefaultRagConfig instance or None if not found
        """
        return self.db.query(DefaultRagConfig).filter(DefaultRagConfig.user_id == user_id).first()

    def update(
        self,
        user_id: int,
        embedding_model: str | None = None,
        embedding_dim: int | None = None,
        retriever_type: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        top_k: int | None = None,
        rerank_enabled: bool | None = None,
        rerank_model: str | None = None,
    ) -> DefaultRagConfig | None:
        """
        Update default RAG configuration for a user.

        Args:
            user_id: User ID
            embedding_model: Optional new embedding model name
            embedding_dim: Optional new embedding dimension
            retriever_type: Optional new retriever type
            chunk_size: Optional new chunk size
            chunk_overlap: Optional new chunk overlap
            top_k: Optional new top_k value
            rerank_enabled: Optional new rerank enabled flag
            rerank_model: Optional new rerank model name

        Returns:
            Updated DefaultRagConfig instance or None if not found
        """
        config = self.get_by_user_id(user_id)
        if not config:
            return None

        if embedding_model is not None:
            config.embedding_model = embedding_model
        if embedding_dim is not None:
            config.embedding_dim = embedding_dim
        if retriever_type is not None:
            config.retriever_type = retriever_type
        if chunk_size is not None:
            config.chunk_size = chunk_size
        if chunk_overlap is not None:
            config.chunk_overlap = chunk_overlap
        if top_k is not None:
            config.top_k = top_k
        if rerank_enabled is not None:
            config.rerank_enabled = rerank_enabled
        if rerank_model is not None:
            config.rerank_model = rerank_model

        self.db.commit()
        self.db.refresh(config)
        return config

    def delete(self, user_id: int) -> bool:
        """
        Delete default RAG configuration for a user.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        config = self.get_by_user_id(user_id)
        if not config:
            return False

        self.db.delete(config)
        self.db.commit()
        return True

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
        Create or update default RAG configuration for a user.

        Args:
            user_id: User ID
            embedding_model: Embedding model name
            embedding_dim: Optional embedding dimension
            retriever_type: Retriever type (vector, graph, hybrid)
            chunk_size: Chunk size for text splitting
            chunk_overlap: Overlap between chunks
            top_k: Number of results to retrieve
            rerank_enabled: Whether to enable reranking
            rerank_model: Optional rerank model name

        Returns:
            Created or updated DefaultRagConfig instance
        """
        existing = self.get_by_user_id(user_id)
        if existing:
            return (
                self.update(
                    user_id=user_id,
                    embedding_model=embedding_model,
                    embedding_dim=embedding_dim,
                    retriever_type=retriever_type,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    top_k=top_k,
                    rerank_enabled=rerank_enabled,
                    rerank_model=rerank_model,
                )
                or existing
            )
        else:
            return self.create(
                user_id=user_id,
                embedding_model=embedding_model,
                embedding_dim=embedding_dim,
                retriever_type=retriever_type,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                top_k=top_k,
                rerank_enabled=rerank_enabled,
                rerank_model=rerank_model,
            )
