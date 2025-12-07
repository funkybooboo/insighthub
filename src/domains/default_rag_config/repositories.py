"""PostgreSQL implementation of DefaultRagConfigRepository (single-user system)."""

from datetime import UTC, datetime
from typing import Optional

from src.domains.default_rag_config.models import (
    DefaultGraphRagConfig,
    DefaultRagConfig,
    DefaultVectorRagConfig,
)
from src.infrastructure.sql_database import SqlDatabase


class DefaultRagConfigRepository:
    """PostgreSQL implementation of default RAG configs repository (single-user system)."""

    def __init__(self, db: SqlDatabase) -> None:
        self.db = db

    def get(self) -> Optional[DefaultRagConfig]:
        """Get the default RAG config (single row)."""
        query = """
            SELECT id, rag_type,
                   vector_embedding_algorithm, vector_chunking_algorithm, vector_rerank_algorithm,
                   vector_chunk_size, vector_chunk_overlap, vector_top_k,
                   vector_embedding_model_vector_size, vector_distance_metric,
                   graph_entity_extraction_algorithm, graph_relationship_extraction_algorithm, graph_clustering_algorithm,
                   graph_entity_types, graph_relationship_types, graph_max_traversal_depth,
                   graph_top_k_entities, graph_top_k_communities, graph_include_entity_neighborhoods,
                   graph_community_min_size, graph_clustering_resolution, graph_clustering_max_level,
                   created_at, updated_at
            FROM default_rag_configs WHERE id = 1
        """
        result = self.db.fetch_one(query, ())
        if result:
            vector_config = DefaultVectorRagConfig(
                embedding_algorithm=result["vector_embedding_algorithm"],
                chunking_algorithm=result["vector_chunking_algorithm"],
                rerank_algorithm=result["vector_rerank_algorithm"],
                chunk_size=result["vector_chunk_size"],
                chunk_overlap=result["vector_chunk_overlap"],
                top_k=result["vector_top_k"],
                embedding_model_vector_size=result["vector_embedding_model_vector_size"],
                distance_metric=result["vector_distance_metric"],
            )

            graph_config = DefaultGraphRagConfig(
                entity_extraction_algorithm=result["graph_entity_extraction_algorithm"],
                relationship_extraction_algorithm=result["graph_relationship_extraction_algorithm"],
                clustering_algorithm=result["graph_clustering_algorithm"],
                entity_types=result["graph_entity_types"],
                relationship_types=result["graph_relationship_types"],
                max_traversal_depth=result["graph_max_traversal_depth"],
                top_k_entities=result["graph_top_k_entities"],
                top_k_communities=result["graph_top_k_communities"],
                include_entity_neighborhoods=result["graph_include_entity_neighborhoods"],
                community_min_size=result["graph_community_min_size"],
                clustering_resolution=result["graph_clustering_resolution"],
                clustering_max_level=result["graph_clustering_max_level"],
            )

            return DefaultRagConfig(
                id=result["id"],
                rag_type=result["rag_type"],
                vector_config=vector_config,
                graph_config=graph_config,
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        return None

    def update(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Update the default RAG config (single row, id=1)."""
        import json

        query = """
            UPDATE default_rag_configs
            SET rag_type = %s,
                vector_embedding_algorithm = %s, vector_chunking_algorithm = %s, vector_rerank_algorithm = %s,
                vector_chunk_size = %s, vector_chunk_overlap = %s, vector_top_k = %s,
                vector_embedding_model_vector_size = %s, vector_distance_metric = %s,
                graph_entity_extraction_algorithm = %s, graph_relationship_extraction_algorithm = %s, graph_clustering_algorithm = %s,
                graph_entity_types = %s, graph_relationship_types = %s, graph_max_traversal_depth = %s,
                graph_top_k_entities = %s, graph_top_k_communities = %s, graph_include_entity_neighborhoods = %s,
                graph_community_min_size = %s, graph_clustering_resolution = %s, graph_clustering_max_level = %s,
                updated_at = %s
            WHERE id = 1
        """
        self.db.execute(
            query,
            (
                config.rag_type,
                config.vector_config.embedding_algorithm,
                config.vector_config.chunking_algorithm,
                config.vector_config.rerank_algorithm,
                config.vector_config.chunk_size,
                config.vector_config.chunk_overlap,
                config.vector_config.top_k,
                config.vector_config.embedding_model_vector_size,
                config.vector_config.distance_metric,
                config.graph_config.entity_extraction_algorithm,
                config.graph_config.relationship_extraction_algorithm,
                config.graph_config.clustering_algorithm,
                json.dumps(config.graph_config.entity_types),
                json.dumps(config.graph_config.relationship_types),
                config.graph_config.max_traversal_depth,
                config.graph_config.top_k_entities,
                config.graph_config.top_k_communities,
                config.graph_config.include_entity_neighborhoods,
                config.graph_config.community_min_size,
                config.graph_config.clustering_resolution,
                config.graph_config.clustering_max_level,
                datetime.now(UTC),
            ),
        )
        return config
