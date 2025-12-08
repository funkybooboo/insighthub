"""Centralized RAG implementation options from factories.

This module provides a single source of truth for all available RAG implementation
options by pulling them directly from the factories. This ensures that CLI prompts,
validation, and configuration all use the same set of available options.
"""

from src.infrastructure.rag.steps.general.chunking.factory import get_available_chunkers
from src.infrastructure.rag.steps.vector_rag.embedding.factory import get_available_embedders
from src.infrastructure.rag.steps.vector_rag.reranking.factory import get_available_rerankers


# RAG Type Options
def get_rag_type_options() -> list[dict[str, str]]:
    """Get available RAG type options.

    Returns:
        List of dicts with 'value', 'label', and 'description' keys
    """
    return [
        {
            "value": "vector",
            "label": "Vector RAG",
            "description": "Traditional vector similarity search with embeddings",
        },
        {
            "value": "graph",
            "label": "Graph RAG",
            "description": "Knowledge graph-based retrieval with entity relationships",
        },
        {
            "value": "hybrid",
            "label": "Hybrid RAG",
            "description": "Combines vector and graph retrieval for enhanced results",
        },
    ]


def get_chunking_options() -> list[dict[str, str]]:
    """Get available chunking algorithm options.

    Returns:
        List of dicts with 'value', 'label', and 'description' keys
    """
    return get_available_chunkers()


def get_embedding_options() -> list[dict[str, str]]:
    """Get available embedding algorithm options.

    Returns:
        List of dicts with 'value', 'label', and 'description' keys
    """
    return get_available_embedders()


def get_reranking_options() -> list[dict[str, str]]:
    """Get available reranking algorithm options.

    Returns:
        List of dicts with 'value', 'label', and 'description' keys
    """
    return get_available_rerankers()


def get_graph_entity_extraction_options() -> list[dict[str, str]]:
    """Get available entity extraction algorithm options for graph RAG.

    Returns:
        List of dicts with 'value', 'label', and 'description' keys
    """
    from src.infrastructure.rag.steps.graph_rag.entity_extraction.factory import (
        EntityExtractorFactory,
    )

    return EntityExtractorFactory.get_available_extractors()


def get_graph_relationship_extraction_options() -> list[dict[str, str]]:
    """Get available relationship extraction algorithm options for graph RAG.

    Returns:
        List of dicts with 'value', 'label', and 'description' keys
    """
    from src.infrastructure.rag.steps.graph_rag.relationship_extraction.factory import (
        RelationshipExtractorFactory,
    )

    return RelationshipExtractorFactory.get_available_extractors()


def get_graph_clustering_options() -> list[dict[str, str]]:
    """Get available clustering algorithm options for graph RAG.

    Returns:
        List of dicts with 'value', 'label', and 'description' keys
    """
    from src.infrastructure.rag.steps.graph_rag.clustering.factory import CommunityDetectorFactory

    return CommunityDetectorFactory.get_available_detectors()


# Convenience functions to get default values
def get_default_rag_type() -> str:
    """Get default RAG type."""
    options = get_rag_type_options()
    return options[0]["value"] if options else "vector"


def get_default_chunking_algorithm() -> str:
    """Get default chunking algorithm."""
    options = get_chunking_options()
    return options[0]["value"] if options else "sentence"


def get_default_embedding_algorithm() -> str:
    """Get default embedding algorithm."""
    options = get_embedding_options()
    return options[0]["value"] if options else "nomic-embed-text"


def get_default_reranking_algorithm() -> str:
    """Get default reranking algorithm."""
    return "none"  # No reranking by default


def get_default_entity_extraction_algorithm() -> str:
    """Get default entity extraction algorithm."""
    options = get_graph_entity_extraction_options()
    return options[0]["value"] if options else "spacy"


def get_default_relationship_extraction_algorithm() -> str:
    """Get default relationship extraction algorithm."""
    options = get_graph_relationship_extraction_options()
    return options[0]["value"] if options else "dependency-parsing"


def get_default_clustering_algorithm() -> str:
    """Get default clustering algorithm."""
    options = get_graph_clustering_options()
    return options[0]["value"] if options else "leiden"


# Validation functions
def is_valid_rag_type(rag_type: str) -> bool:
    """Check if RAG type is valid."""
    valid_values = [opt["value"] for opt in get_rag_type_options()]
    return rag_type in valid_values


def get_valid_rag_types() -> list[str]:
    """Get list of valid RAG type values."""
    return [opt["value"] for opt in get_rag_type_options()]


def is_valid_chunking_algorithm(algorithm: str) -> bool:
    """Check if chunking algorithm is valid."""
    valid_values = [opt["value"] for opt in get_chunking_options()]
    return algorithm in valid_values


def is_valid_embedding_algorithm(algorithm: str) -> bool:
    """Check if embedding algorithm is valid."""
    valid_values = [opt["value"] for opt in get_embedding_options()]
    return algorithm in valid_values


def is_valid_reranking_algorithm(algorithm: str) -> bool:
    """Check if reranking algorithm is valid."""
    valid_values = [opt["value"] for opt in get_reranking_options()]
    return algorithm in valid_values


def is_valid_entity_extraction_algorithm(algorithm: str) -> bool:
    """Check if entity extraction algorithm is valid."""
    valid_values = [opt["value"] for opt in get_graph_entity_extraction_options()]
    return algorithm in valid_values


def is_valid_relationship_extraction_algorithm(algorithm: str) -> bool:
    """Check if relationship extraction algorithm is valid."""
    valid_values = [opt["value"] for opt in get_graph_relationship_extraction_options()]
    return algorithm in valid_values


def is_valid_clustering_algorithm(algorithm: str) -> bool:
    """Check if clustering algorithm is valid."""
    valid_values = [opt["value"] for opt in get_graph_clustering_options()]
    return algorithm in valid_values
