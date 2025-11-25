"""SQL repository for default RAG configurations."""

from shared.database.sql import SqlDatabase
from shared.models.default_rag_config import DefaultRagConfig

from .default_rag_config_repository import DefaultRagConfigRepository


class SqlDefaultRagConfigRepository(DefaultRagConfigRepository):
    """SQL implementation of default RAG config repository."""

    def __init__(self, db: SqlDatabase):
        """Initialize repository with database connection."""
        self.db = db

    def get_by_user_id(self, user_id: int) -> DefaultRagConfig | None:
        """Get default RAG config for a user."""
        query = """
            SELECT id, user_id, embedding_model, embedding_dim, retriever_type,
                   chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_model,
                   created_at, updated_at
            FROM default_rag_configs
            WHERE user_id = %s
        """
        result = self.db.fetchone(query, {"user_id": user_id})
        if result:
            return DefaultRagConfig(
                id=result["id"],
                user_id=result["user_id"],
                embedding_model=result["embedding_model"],
                embedding_dim=result["embedding_dim"],
                retriever_type=result["retriever_type"],
                chunk_size=result["chunk_size"],
                chunk_overlap=result["chunk_overlap"],
                top_k=result["top_k"],
                rerank_enabled=result["rerank_enabled"],
                rerank_model=result["rerank_model"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        return None

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
        # First try to update existing record
        update_query = """
            UPDATE default_rag_configs
            SET embedding_model = %s, embedding_dim = %s, retriever_type = %s,
                chunk_size = %s, chunk_overlap = %s, top_k = %s,
                rerank_enabled = %s, rerank_model = %s, updated_at = NOW()
            WHERE user_id = %s
            RETURNING id, user_id, embedding_model, embedding_dim, retriever_type,
                      chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_model,
                      created_at, updated_at
        """
        result = self.db.fetchone(
            update_query,
            {
                "embedding_model": embedding_model,
                "embedding_dim": embedding_dim,
                "retriever_type": retriever_type,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "top_k": top_k,
                "rerank_enabled": rerank_enabled,
                "rerank_model": rerank_model,
                "user_id": user_id,
            },
        )

        if result:
            # Update succeeded
            return DefaultRagConfig(
                id=result["id"],
                user_id=result["user_id"],
                embedding_model=result["embedding_model"],
                embedding_dim=result["embedding_dim"],
                retriever_type=result["retriever_type"],
                chunk_size=result["chunk_size"],
                chunk_overlap=result["chunk_overlap"],
                top_k=result["top_k"],
                rerank_enabled=result["rerank_enabled"],
                rerank_model=result["rerank_model"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

        # No existing record, create new one
        insert_query = """
            INSERT INTO default_rag_configs (
                user_id, embedding_model, embedding_dim, retriever_type,
                chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_model
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, embedding_model, embedding_dim, retriever_type,
                      chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_model,
                      created_at, updated_at
        """
        result = self.db.fetchone(
            insert_query,
            {
                "user_id": user_id,
                "embedding_model": embedding_model,
                "embedding_dim": embedding_dim,
                "retriever_type": retriever_type,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "top_k": top_k,
                "rerank_enabled": rerank_enabled,
                "rerank_model": rerank_model,
            },
        )

        if result:
            return DefaultRagConfig(
                id=result["id"],
                user_id=result["user_id"],
                embedding_model=result["embedding_model"],
                embedding_dim=result["embedding_dim"],
                retriever_type=result["retriever_type"],
                chunk_size=result["chunk_size"],
                chunk_overlap=result["chunk_overlap"],
                top_k=result["top_k"],
                rerank_enabled=result["rerank_enabled"],
                rerank_model=result["rerank_model"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

        raise RuntimeError("Failed to create or update default RAG config")

    def delete_by_user_id(self, user_id: int) -> bool:
        """Delete default RAG config for a user."""
        query = "DELETE FROM default_rag_configs WHERE user_id = %s"
        self.db.execute(query, {"user_id": user_id})
        return True
