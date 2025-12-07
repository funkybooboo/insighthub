"""Default RAG configuration mappers."""

from src.domains.default_rag_config.dtos import (
    DefaultRagConfigResponse,
    GraphRagConfigResponse,
    VectorRagConfigResponse,
)
from src.domains.default_rag_config.models import DefaultRagConfig
from src.infrastructure.mappers import map_timestamps


class DefaultRagConfigMapper:
    """Mapper for converting between DefaultRagConfig models and Response DTOs."""

    @staticmethod
    def to_response(config: DefaultRagConfig) -> DefaultRagConfigResponse:
        """
        Convert DefaultRagConfig model to Response DTO.

        Args:
            config: DefaultRagConfig model instance

        Returns:
            DefaultRagConfigResponse instance
        """
        created_at_str, updated_at_str = map_timestamps(config.created_at, config.updated_at)
        return DefaultRagConfigResponse(
            id=config.id,
            rag_type=config.rag_type,
            vector_config=VectorRagConfigResponse(
                embedding_model_vector_size=config.vector_config.embedding_model_vector_size,
                distance_metric=config.vector_config.distance_metric,
                embedding_algorithm=config.vector_config.embedding_algorithm,
                chunking_algorithm=config.vector_config.chunking_algorithm,
                rerank_algorithm=config.vector_config.rerank_algorithm,
                chunk_size=config.vector_config.chunk_size,
                chunk_overlap=config.vector_config.chunk_overlap,
                top_k=config.vector_config.top_k,
            ),
            graph_config=GraphRagConfigResponse(
                entity_extraction_algorithm=config.graph_config.entity_extraction_algorithm,
                relationship_extraction_algorithm=config.graph_config.relationship_extraction_algorithm,
                clustering_algorithm=config.graph_config.clustering_algorithm,
                entity_types=config.graph_config.entity_types,
                relationship_types=config.graph_config.relationship_types,
                max_traversal_depth=config.graph_config.max_traversal_depth,
                top_k_entities=config.graph_config.top_k_entities,
                top_k_communities=config.graph_config.top_k_communities,
                include_entity_neighborhoods=config.graph_config.include_entity_neighborhoods,
                community_min_size=config.graph_config.community_min_size,
                clustering_resolution=config.graph_config.clustering_resolution,
                clustering_max_level=config.graph_config.clustering_max_level,
            ),
            created_at=created_at_str,
            updated_at=updated_at_str,
        )
