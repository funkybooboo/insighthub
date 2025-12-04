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

    # Validate vector config if rag_type is vector
    if rag_type == "vector":
        if request.chunking_algorithm and not is_valid_chunking_algorithm(
            request.chunking_algorithm
        ):
            return Failure(
                ValidationError(
                    f"Invalid chunking algorithm '{request.chunking_algorithm}'",
                    field="chunking_algorithm",
                )
            )

        if request.chunk_size is not None:
            if request.chunk_size <= 0:
                return Failure(
                    ValidationError("Chunk size must be a positive integer", field="chunk_size")
                )

        if request.chunk_overlap is not None:
            if request.chunk_overlap < 0:
                return Failure(
                    ValidationError(
                        "Chunk overlap must be a non-negative integer", field="chunk_overlap"
                    )
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

        if request.top_k is not None:
            if request.top_k <= 0:
                return Failure(ValidationError("Top K must be a positive integer", field="top_k"))

        if request.rerank_algorithm and not is_valid_reranking_algorithm(request.rerank_algorithm):
            return Failure(
                ValidationError(
                    f"Invalid reranking algorithm '{request.rerank_algorithm}'",
                    field="rerank_algorithm",
                )
            )

    # Validate graph config if rag_type is graph
    elif rag_type == "graph":
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

    # Return cleaned request
    return Success(
        CreateUpdateDefaultRagConfigRequest(
            rag_type=rag_type,
            chunking_algorithm=request.chunking_algorithm,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            embedding_algorithm=request.embedding_algorithm,
            top_k=request.top_k,
            rerank_algorithm=request.rerank_algorithm,
            entity_extraction_algorithm=request.entity_extraction_algorithm,
            relationship_extraction_algorithm=request.relationship_extraction_algorithm,
            clustering_algorithm=request.clustering_algorithm,
        )
    )
