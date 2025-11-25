"""Factory for creating embedding encoder instances."""

from enum import Enum
from typing import Optional

from .ollama_vector_embedding_encoder import OllamaVectorEmbeddingEncoder
from .vector_embedding_encoder import VectorEmbeddingEncoder


class EmbeddingEncoderType(Enum):
    """Enum for embedding encoder implementation types."""

    OLLAMA = "ollama"


def create_embedder_from_config(
    embedding_algorithm: str,
    base_url: str,
    timeout: int = 30,
) -> Optional[VectorEmbeddingEncoder]:
    """
    Create an embedding encoder instance based on algorithm configuration.

    Args:
        embedding_algorithm: Algorithm/model type ("nomic-embed-text", "all-MiniLM-L6-v2", etc.)
        base_url: Ollama server URL
        timeout: Request timeout in seconds (default 30)

    Returns:
        VectorEmbeddingEncoder if creation succeeds, None if algorithm unknown
    """
    # All embedding algorithms currently use Ollama infrastructure
    return OllamaVectorEmbeddingEncoder(
        model=embedding_algorithm,
        base_url=base_url,
        timeout=timeout,
    )
