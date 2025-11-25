"""SQL implementation of Vector RAG configuration repository."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.repositories.vector_rag_config.vector_rag_config_repository import VectorRagConfigRepository
from shared.types.rag import VectorRagConfig


class SqlVectorRagConfigRepository(VectorRagConfigRepository):
    """SQL implementation of VectorRagConfig repository."""

    def __init__(self, db: PostgresSqlDatabase):
        """Initialize the repository."""
        self._db = db

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
        """Create a new Vector RAG configuration for a workspace."""
        query = """
        INSERT INTO vector_rag_configs (
            workspace_id, embedding_algorithm, chunking_algorithm,
            chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_algorithm
        ) VALUES (
            %(workspace_id)s, %(embedding_algorithm)s, %(chunking_algorithm)s,
            %(chunk_size)s, %(chunk_overlap)s, %(top_k)s, %(rerank_enabled)s, %(rerank_algorithm)s
        )
        RETURNING id, workspace_id, embedding_algorithm, chunking_algorithm,
                 chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_algorithm,
                 created_at, updated_at
        """

        params = {
            "workspace_id": workspace_id,
            "embedding_algorithm": embedding_algorithm,
            "chunking_algorithm": chunking_algorithm,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "top_k": top_k,
            "rerank_enabled": rerank_enabled,
            "rerank_algorithm": rerank_algorithm,
        }

        row = self._db.fetchone(query, params)
        if row is None:
            raise RuntimeError("Failed to create vector RAG config")

        return VectorRagConfig(**row)

    def get_vector_rag_config(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get Vector RAG configuration for a workspace."""
        query = """
        SELECT id, workspace_id, embedding_algorithm, chunking_algorithm,
               chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_algorithm,
               created_at, updated_at
        FROM vector_rag_configs
        WHERE workspace_id = %(workspace_id)s
        """

        row = self._db.fetchone(query, {"workspace_id": workspace_id})
        if row is None:
            return None

        return VectorRagConfig(**row)

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
        """Update Vector RAG configuration for a workspace."""
        # Build dynamic update query
        update_fields = []
        params: dict = {"workspace_id": workspace_id}

        if embedding_algorithm is not None:
            update_fields.append("embedding_algorithm = %(embedding_algorithm)s")
            params["embedding_algorithm"] = embedding_algorithm
        if chunking_algorithm is not None:
            update_fields.append("chunking_algorithm = %(chunking_algorithm)s")
            params["chunking_algorithm"] = chunking_algorithm
        if chunk_size is not None:
            update_fields.append("chunk_size = %(chunk_size)s")
            params["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            update_fields.append("chunk_overlap = %(chunk_overlap)s")
            params["chunk_overlap"] = chunk_overlap
        if top_k is not None:
            update_fields.append("top_k = %(top_k)s")
            params["top_k"] = top_k
        if rerank_enabled is not None:
            update_fields.append("rerank_enabled = %(rerank_enabled)s")
            params["rerank_enabled"] = rerank_enabled
        if rerank_algorithm is not None:
            update_fields.append("rerank_algorithm = %(rerank_algorithm)s")
            params["rerank_algorithm"] = rerank_algorithm

        if not update_fields:
            return self.get_vector_rag_config(workspace_id)

        update_fields.append("updated_at = NOW()")

        query = f"""
        UPDATE vector_rag_configs
        SET {', '.join(update_fields)}
        WHERE workspace_id = %(workspace_id)s
        RETURNING id, workspace_id, embedding_algorithm, chunking_algorithm,
                 chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_algorithm,
                 created_at, updated_at
        """

        row = self._db.fetchone(query, params)
        if row is None:
            return None

        return VectorRagConfig(**row)

    def delete_vector_rag_config(self, workspace_id: int) -> bool:
        """Delete Vector RAG configuration for a workspace."""
        query = "DELETE FROM vector_rag_configs WHERE workspace_id = %(workspace_id)s"
        self._db.execute(query, {"workspace_id": workspace_id})
        return True