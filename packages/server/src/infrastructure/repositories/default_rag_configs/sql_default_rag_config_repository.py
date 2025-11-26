"""SQL implementation of DefaultRagConfigRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.database import SqlDatabase
from src.infrastructure.models import DefaultGraphRagConfig, DefaultRagConfig, DefaultVectorRagConfig

from .default_rag_config_repository import DefaultRagConfigRepository


class SqlDefaultRagConfigRepository(DefaultRagConfigRepository):
    """SQL implementation of default RAG configs repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[DefaultRagConfig]:
        """Get default RAG config for a user."""
        query = """
            SELECT id, user_id,
                   vector_embedding_algorithm, vector_chunking_algorithm, vector_rerank_algorithm,
                   vector_chunk_size, vector_chunk_overlap, vector_top_k,
                   graph_entity_extraction_algorithm, graph_relationship_extraction_algorithm, graph_clustering_algorithm,
                   created_at, updated_at
            FROM default_rag_configs WHERE user_id = %s
        """
        result = self.db.fetch_one(query, (user_id,))
        if result:
            # Extract vector config fields
            vector_config = {
                "embedding_algorithm": result.get("vector_embedding_algorithm", "ollama"),
                "chunking_algorithm": result.get("vector_chunking_algorithm", "sentence"),
                "rerank_algorithm": result.get("vector_rerank_algorithm", "none"),
                "chunk_size": result.get("vector_chunk_size", 1000),
                "chunk_overlap": result.get("vector_chunk_overlap", 200),
                "top_k": result.get("vector_top_k", 5),
            }

            # Extract graph config fields
            graph_config = {
                "entity_extraction_algorithm": result.get("graph_entity_extraction_algorithm", "spacy"),
                "relationship_extraction_algorithm": result.get("graph_relationship_extraction_algorithm", "dependency-parsing"),
                "clustering_algorithm": result.get("graph_clustering_algorithm", "leiden"),
            }

            return DefaultRagConfig(
                id=result["id"],
                user_id=result["user_id"],
                vector_config=DefaultVectorRagConfig(**vector_config),
                graph_config=DefaultGraphRagConfig(**graph_config),
                created_at=result.get("created_at") or datetime.utcnow(),
                updated_at=result.get("updated_at") or datetime.utcnow(),
            )
        return None

    def create(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Create a new default RAG config."""
        query = """
            INSERT INTO default_rag_configs (
                user_id,
                vector_embedding_algorithm, vector_chunking_algorithm, vector_rerank_algorithm,
                vector_chunk_size, vector_chunk_overlap, vector_top_k,
                graph_entity_extraction_algorithm, graph_relationship_extraction_algorithm, graph_clustering_algorithm,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.fetch_one(
            query,
            (
                config.user_id,
                config.vector_config.embedding_algorithm,
                config.vector_config.chunking_algorithm,
                config.vector_config.rerank_algorithm,
                config.vector_config.chunk_size,
                config.vector_config.chunk_overlap,
                config.vector_config.top_k,
                config.graph_config.entity_extraction_algorithm,
                config.graph_config.relationship_extraction_algorithm,
                config.graph_config.clustering_algorithm,
                datetime.utcnow(),
                datetime.utcnow(),
            ),
        )

        if result:
            config.id = result["id"]
            return config

        raise RuntimeError("Failed to create default RAG config")

    def update(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Update an existing default RAG config."""
        query = """
            UPDATE default_rag_configs
            SET vector_embedding_algorithm = %s, vector_chunking_algorithm = %s, vector_rerank_algorithm = %s,
                vector_chunk_size = %s, vector_chunk_overlap = %s, vector_top_k = %s,
                graph_entity_extraction_algorithm = %s, graph_relationship_extraction_algorithm = %s, graph_clustering_algorithm = %s,
                updated_at = %s
            WHERE user_id = %s
        """
        affected_rows = self.db.execute(
            query,
            (
                config.vector_config.embedding_algorithm,
                config.vector_config.chunking_algorithm,
                config.vector_config.rerank_algorithm,
                config.vector_config.chunk_size,
                config.vector_config.chunk_overlap,
                config.vector_config.top_k,
                config.graph_config.entity_extraction_algorithm,
                config.graph_config.relationship_extraction_algorithm,
                config.graph_config.clustering_algorithm,
                datetime.utcnow(),
                config.user_id,
            ),
        )

        if affected_rows == 0:
            raise RuntimeError("Failed to update default RAG config")

        return config

    def delete_by_user_id(self, user_id: int) -> bool:
        """Delete default RAG config for a user."""
        query = "DELETE FROM default_rag_configs WHERE user_id = %s"
        affected_rows = self.db.execute(query, (user_id,))
        return affected_rows > 0