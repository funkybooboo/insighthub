"""Factory for creating embedding encoder instances."""

from enum import Enum
from typing import Optional

from .ollama_vector_embedding_encoder import OllamaVectorEmbeddingEncoder
from .vector_embedding_encoder import VectorEmbeddingEncoder


class EmbeddingEncoderType(Enum):
    """Enum for embedding encoder implementation types."""

    OLLAMA = "ollama"


def create_embedding_encoder(
    encoder_type: str,
    model: str | None = None,
    base_url: str | None = None,
    timeout: int = 30,
) -> Optional[VectorEmbeddingEncoder]:
    """
    Create an embedding encoder instance based on configuration.

    Args:
        encoder_type: Type of embedding encoder ("ollama")
        model: Model name (required for ollama)
        base_url: Server URL (required for ollama)
        timeout: Request timeout in seconds (default 30)

    Returns:
        VectorEmbeddingEncoder if creation succeeds, None if type unknown or params missing

    Note:
        Additional encoder types (OpenAI, Sentence Transformers) can be
        added here when implemented.
    """
    try:
        encoder_enum = EmbeddingEncoderType(encoder_type)
    except ValueError:
        return None

    if encoder_enum == EmbeddingEncoderType.OLLAMA:
        if model is None or base_url is None:
            return None
        return OllamaVectorEmbeddingEncoder(
            model=model,
            base_url=base_url,
            timeout=timeout,
        )

    return None
