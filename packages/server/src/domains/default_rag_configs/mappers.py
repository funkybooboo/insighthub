"""Default RAG configuration mappers."""

from src.domains.default_rag_configs.dtos import (
    DefaultRagConfigDTO,
    DefaultRagConfigResponseDTO,
    GraphRagConfigDTO,
    VectorRagConfigDTO,
)
from src.infrastructure.models import DefaultRagConfig


class DefaultRagConfigMapper:
    """Mapper for converting between DefaultRagConfig models and DTOs."""

    @staticmethod
    def to_dto(config: DefaultRagConfig) -> DefaultRagConfigDTO:
        """
        Convert DefaultRagConfig model to DTO.

        Args:
            config: DefaultRagConfig model instance

        Returns:
            DefaultRagConfigDTO instance
        """
        return DefaultRagConfigDTO(
            id=config.id,
            user_id=config.user_id,
            vector_config=VectorRagConfigDTO(
                embedding_algorithm=config.vector_config.embedding_algorithm,
                chunking_algorithm=config.vector_config.chunking_algorithm,
                rerank_algorithm=config.vector_config.rerank_algorithm,
                chunk_size=config.vector_config.chunk_size,
                chunk_overlap=config.vector_config.chunk_overlap,
                top_k=config.vector_config.top_k,
            ),
            graph_config=GraphRagConfigDTO(
                entity_extraction_algorithm=config.graph_config.entity_extraction_algorithm,
                relationship_extraction_algorithm=config.graph_config.relationship_extraction_algorithm,
                clustering_algorithm=config.graph_config.clustering_algorithm,
            ),
            created_at=config.created_at.isoformat(),
            updated_at=config.updated_at.isoformat(),
        )

    @staticmethod
    def to_response_dict(config_dto: DefaultRagConfigDTO) -> dict:
        """
        Convert DefaultRagConfigDTO to response dictionary for API.

        Args:
            config_dto: DefaultRagConfigDTO instance

        Returns:
            Dictionary ready for jsonify
        """
        return {
            "id": config_dto.id,
            "user_id": config_dto.user_id,
            "vector_config": {
                "embedding_algorithm": config_dto.vector_config.embedding_algorithm,
                "chunking_algorithm": config_dto.vector_config.chunking_algorithm,
                "rerank_algorithm": config_dto.vector_config.rerank_algorithm,
                "chunk_size": config_dto.vector_config.chunk_size,
                "chunk_overlap": config_dto.vector_config.chunk_overlap,
                "top_k": config_dto.vector_config.top_k,
            },
            "graph_config": {
                "entity_extraction_algorithm": config_dto.graph_config.entity_extraction_algorithm,
                "relationship_extraction_algorithm": config_dto.graph_config.relationship_extraction_algorithm,
                "clustering_algorithm": config_dto.graph_config.clustering_algorithm,
            },
            "created_at": config_dto.created_at,
            "updated_at": config_dto.updated_at,
        }

    @staticmethod
    def vector_config_from_dict(data: dict) -> dict:
        """
        Extract vector config updates from request data.

        Args:
            data: Request data dictionary

        Returns:
            Dictionary with vector config field updates
        """
        vector_config = {}
        if "embedding_algorithm" in data:
            vector_config["embedding_algorithm"] = data["embedding_algorithm"]
        if "chunking_algorithm" in data:
            vector_config["chunking_algorithm"] = data["chunking_algorithm"]
        if "rerank_algorithm" in data:
            vector_config["rerank_algorithm"] = data["rerank_algorithm"]
        if "chunk_size" in data:
            vector_config["chunk_size"] = data["chunk_size"]
        if "chunk_overlap" in data:
            vector_config["chunk_overlap"] = data["chunk_overlap"]
        if "top_k" in data:
            vector_config["top_k"] = data["top_k"]
        return vector_config

    @staticmethod
    def graph_config_from_dict(data: dict) -> dict:
        """
        Extract graph config updates from request data.

        Args:
            data: Request data dictionary

        Returns:
            Dictionary with graph config field updates
        """
        graph_config = {}
        if "entity_extraction_algorithm" in data:
            graph_config["entity_extraction_algorithm"] = data["entity_extraction_algorithm"]
        if "relationship_extraction_algorithm" in data:
            graph_config["relationship_extraction_algorithm"] = data["relationship_extraction_algorithm"]
        if "clustering_algorithm" in data:
            graph_config["clustering_algorithm"] = data["clustering_algorithm"]
        return graph_config