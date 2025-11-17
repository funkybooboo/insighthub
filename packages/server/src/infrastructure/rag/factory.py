"""
Factory for creating RAG instances with different configurations.
"""

from src.infrastructure.rag.rag import Rag
from src.infrastructure.rag.types import RagConfig


def create_rag(config: RagConfig | None = None) -> Rag:
    """
    Factory function to create RAG instances from configuration.

    Args:
        config: Optional RagConfig dictionary. If not provided, defaults are used:
            - rag_type: "vector"
            - chunking_strategy: "sentence"
            - embedding_type: "ollama"
            - vector_store_type: "qdrant"
            - chunk_size: 512
            - chunk_overlap: 50
            - embedding_model_name: "nomic-embed-text"
            - vector_store_host: "localhost"
            - vector_store_port: 6333
            - collection_name: "documents"

    Returns:
        Configured RAG instance implementing the Rag interface.

    Raises:
        ValueError: If the provided configuration is invalid.

    Example:
        >>> config: RagConfig = {
        ...     "rag_type": "vector",
        ...     "chunking_strategy": "sentence",
        ...     "chunk_size": 1024,
        ... }
        >>> rag = create_rag(config)
    """
    # Define default configuration
    defaults: RagConfig = {
        "rag_type": "vector",
        "chunking_strategy": "sentence",
        "embedding_type": "ollama",
        "vector_store_type": "qdrant",
        "chunk_size": 512,
        "chunk_overlap": 50,
        "embedding_model_name": "nomic-embed-text",
        "vector_store_host": "localhost",
        "vector_store_port": 6333,
        "collection_name": "documents",
    }

    # Merge provided config with defaults
    _merged_config: RagConfig = {**defaults, **config} if config else defaults

    # TODO: Validate _merged_config values (e.g., rag_type in allowed options)
    # TODO: Instantiate embedding model, vector store, and RAG system based on _merged_config
    # TODO: Return fully configured Rag instance

    raise NotImplementedError("Factory implementation pending")
