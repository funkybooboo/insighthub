"""Default RAG configuration input validation."""

from returns.result import Failure, Result, Success

from src.domains.default_rag_config.dtos import CreateUpdateDefaultRagConfigRequest
from src.infrastructure.rag.options import (
    get_valid_rag_types,
    is_valid_chunking_algorithm,
    is_valid_clustering_algorithm,
    is_valid_embedding_algorithm,
    is_valid_entity_extraction_algorithm,
    is_valid_rag_type,
    is_valid_relationship_extraction_algorithm,
    is_valid_reranking_algorithm,
)
from src.infrastructure.types import ValidationError


def _validate_vector_config(
    request: CreateUpdateDefaultRagConfigRequest,
) -> Result[None, ValidationError]:
    """Validate vector configuration fields."""
    if request.chunking_algorithm and not is_valid_chunking_algorithm(request.chunking_algorithm):
        return Failure(
            ValidationError(
                f"Invalid chunking algorithm '{request.chunking_algorithm}'",
                field="chunking_algorithm",
            )
        )

    if request.chunk_size is not None and request.chunk_size <= 0:
        return Failure(ValidationError("Chunk size must be a positive integer", field="chunk_size"))

    if request.chunk_overlap is not None and request.chunk_overlap < 0:
        return Failure(
            ValidationError("Chunk overlap must be a non-negative integer", field="chunk_overlap")
        )

    if request.embedding_algorithm and not is_valid_embedding_algorithm(
        request.embedding_algorithm
    ):
        return Failure(
            ValidationError(
                f"Invalid embedding algorithm '{request.embedding_algorithm}'",
                field="embedding_algorithm",
            )
        )

    if request.top_k is not None and request.top_k <= 0:
        return Failure(ValidationError("Top K must be a positive integer", field="top_k"))

    if request.rerank_algorithm and not is_valid_reranking_algorithm(request.rerank_algorithm):
        return Failure(
            ValidationError(
                f"Invalid reranking algorithm '{request.rerank_algorithm}'",
                field="rerank_algorithm",
            )
        )

    return Success(None)


def _validate_graph_config(
    request: CreateUpdateDefaultRagConfigRequest,
) -> Result[None, ValidationError]:
    """Validate graph configuration fields."""
    if request.entity_extraction_algorithm and not is_valid_entity_extraction_algorithm(
        request.entity_extraction_algorithm
    ):
        return Failure(
            ValidationError(
                f"Invalid entity extraction algorithm '{request.entity_extraction_algorithm}'",
                field="entity_extraction_algorithm",
            )
        )

    if (
        request.relationship_extraction_algorithm
        and not is_valid_relationship_extraction_algorithm(
            request.relationship_extraction_algorithm
        )
    ):
        return Failure(
            ValidationError(
                f"Invalid relationship extraction algorithm '{request.relationship_extraction_algorithm}'",
                field="relationship_extraction_algorithm",
            )
        )

    if request.clustering_algorithm and not is_valid_clustering_algorithm(
        request.clustering_algorithm
    ):
        return Failure(
            ValidationError(
                f"Invalid clustering algorithm '{request.clustering_algorithm}'",
                field="clustering_algorithm",
            )
        )

    # Validate entity_types
    if request.entity_types is not None:
        if not isinstance(request.entity_types, list):
            return Failure(ValidationError("entity_types must be a list", field="entity_types"))
        if len(request.entity_types) == 0:
            return Failure(ValidationError("entity_types must not be empty", field="entity_types"))

    # Validate relationship_types
    if request.relationship_types is not None:
        if not isinstance(request.relationship_types, list):
            return Failure(
                ValidationError("relationship_types must be a list", field="relationship_types")
            )
        if len(request.relationship_types) == 0:
            return Failure(
                ValidationError("relationship_types must not be empty", field="relationship_types")
            )

    # Validate max_traversal_depth
    if request.max_traversal_depth is not None and request.max_traversal_depth <= 0:
        return Failure(
            ValidationError(
                "max_traversal_depth must be a positive integer", field="max_traversal_depth"
            )
        )

    # Validate top_k_entities
    if request.top_k_entities is not None and request.top_k_entities <= 0:
        return Failure(
            ValidationError("top_k_entities must be a positive integer", field="top_k_entities")
        )

    # Validate top_k_communities
    if request.top_k_communities is not None and request.top_k_communities <= 0:
        return Failure(
            ValidationError(
                "top_k_communities must be a positive integer", field="top_k_communities"
            )
        )

    # Validate community_min_size
    if request.community_min_size is not None and request.community_min_size <= 0:
        return Failure(
            ValidationError(
                "community_min_size must be a positive integer", field="community_min_size"
            )
        )

    # Validate clustering_resolution
    if request.clustering_resolution is not None and request.clustering_resolution <= 0:
        return Failure(
            ValidationError(
                "clustering_resolution must be a positive float", field="clustering_resolution"
            )
        )

    # Validate clustering_max_level
    if request.clustering_max_level is not None and request.clustering_max_level <= 0:
        return Failure(
            ValidationError(
                "clustering_max_level must be a positive integer", field="clustering_max_level"
            )
        )

    return Success(None)


def validate_create_update_default_rag_config(
    request: CreateUpdateDefaultRagConfigRequest,
    default_rag_type: str = "vector",
) -> Result[CreateUpdateDefaultRagConfigRequest, ValidationError]:
    """Validate and clean default RAG configuration input.

    Args:
        request: Raw user input request
        default_rag_type: Default RAG type to use if not provided

    Returns:
        Result with cleaned CreateUpdateDefaultRagConfigRequest or ValidationError
    """
    # Validate and default RAG type
    rag_type = request.rag_type or default_rag_type
    if not is_valid_rag_type(rag_type):
        valid_types = get_valid_rag_types()
        return Failure(
            ValidationError(
                f"Invalid rag_type. Must be one of: {', '.join(valid_types)}",
                field="rag_type",
            )
        )

    # Validate config based on rag_type
    if rag_type == "vector":
        validation_result = _validate_vector_config(request)
        if isinstance(validation_result, Failure):
            return validation_result
    elif rag_type == "graph":
        validation_result = _validate_graph_config(request)
        if isinstance(validation_result, Failure):
            return validation_result

    # Return cleaned request
    return Success(
        CreateUpdateDefaultRagConfigRequest(
            rag_type=rag_type,
            chunking_algorithm=request.chunking_algorithm,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            embedding_algorithm=request.embedding_algorithm,
            embedding_model_vector_size=request.embedding_model_vector_size,
            distance_metric=request.distance_metric,
            top_k=request.top_k,
            rerank_algorithm=request.rerank_algorithm,
            entity_extraction_algorithm=request.entity_extraction_algorithm,
            relationship_extraction_algorithm=request.relationship_extraction_algorithm,
            clustering_algorithm=request.clustering_algorithm,
            entity_types=request.entity_types,
            relationship_types=request.relationship_types,
            max_traversal_depth=request.max_traversal_depth,
            top_k_entities=request.top_k_entities,
            top_k_communities=request.top_k_communities,
            include_entity_neighborhoods=request.include_entity_neighborhoods,
            community_min_size=request.community_min_size,
            clustering_resolution=request.clustering_resolution,
            clustering_max_level=request.clustering_max_level,
        )
    )
