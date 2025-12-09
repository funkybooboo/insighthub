"""Default RAG configuration domain orchestrator.

Eliminates duplication between commands.py and routes.py by providing
a single interface for: Request DTO -> Validation -> Service -> Response DTO
"""

from typing import Dict

from returns.result import Failure, Result, Success

from src.domains.default_rag_config.dtos import (
    CreateUpdateDefaultRagConfigRequest,
    DefaultRagConfigResponse,
)
from src.domains.default_rag_config.mappers import DefaultRagConfigMapper
from src.domains.default_rag_config.service import DefaultRagConfigService
from src.domains.default_rag_config.validation import validate_create_update_default_rag_config
from src.infrastructure.types import ValidationError


class DefaultRagConfigOrchestrator:
    """Orchestrates default RAG config operations: validation -> service -> response."""

    def __init__(self, service: DefaultRagConfigService):
        """Initialize orchestrator with service."""
        self.service = service

    def get_config(self) -> Result[DefaultRagConfigResponse, None]:
        """Get default RAG configuration.

        Returns:
            Result with DefaultRagConfigResponse or None if not found
        """
        # Call service
        config = self.service.get_config()

        # Auto-create if doesn't exist
        if not config:
            config = self.service.create_or_update_config(
                rag_type="vector",
                vector_config={},
                graph_config={},
            )

        # Map to response
        return Success(DefaultRagConfigMapper.to_response(config))

    def create_or_update_config(
        self,
        request: CreateUpdateDefaultRagConfigRequest,
        default_rag_type: str = "vector",
    ) -> Result[DefaultRagConfigResponse, ValidationError]:
        """Orchestrate create/update default RAG configuration.

        Args:
            request: Create/update config request DTO
            default_rag_type: Default RAG type if not specified

        Returns:
            Result with DefaultRagConfigResponse or error
        """
        # Validate
        validation_result = validate_create_update_default_rag_config(request, default_rag_type)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Validation guarantees rag_type is not None
        assert validated_request.rag_type is not None

        # Build config dicts for service
        vector_config: Dict[str, str | int] = {}
        graph_config: Dict[str, str] = {}

        if validated_request.rag_type == "vector":
            if validated_request.chunking_algorithm:
                vector_config["chunking_algorithm"] = validated_request.chunking_algorithm
            if validated_request.chunk_size is not None:
                vector_config["chunk_size"] = validated_request.chunk_size
            if validated_request.chunk_overlap is not None:
                vector_config["chunk_overlap"] = validated_request.chunk_overlap
            if validated_request.embedding_algorithm:
                vector_config["embedding_algorithm"] = validated_request.embedding_algorithm
            if validated_request.top_k is not None:
                vector_config["top_k"] = validated_request.top_k
            if validated_request.rerank_algorithm:
                vector_config["rerank_algorithm"] = validated_request.rerank_algorithm
        else:  # graph
            if validated_request.entity_extraction_algorithm:
                graph_config["entity_extraction_algorithm"] = (
                    validated_request.entity_extraction_algorithm
                )
            if validated_request.relationship_extraction_algorithm:
                graph_config["relationship_extraction_algorithm"] = (
                    validated_request.relationship_extraction_algorithm
                )
            if validated_request.clustering_algorithm:
                graph_config["clustering_algorithm"] = validated_request.clustering_algorithm

        # Call service
        config = self.service.create_or_update_config(
            rag_type=validated_request.rag_type,
            vector_config=vector_config,
            graph_config=graph_config,
        )

        # Map to response
        return Success(DefaultRagConfigMapper.to_response(config))
