"""Factory for creating embedding encoder instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

from .vector_embedding_encoder import VectorEmbeddingEncoder
from .ollama_vector_embedding_encoder import OllamaVectorEmbeddingEncoder


class EmbeddingEncoderType(Enum):
    """Enum for embedding encoder implementation types."""

    OLLAMA = "ollama"


def create_embedding_encoder(
    encoder_type: str,
    model: str | None = None,
    base_url: str | None = None,
    timeout: int = 30,
) -> Option[VectorEmbeddingEncoder]:
    """
    Create an embedding encoder instance based on configuration.

    Args:
        encoder_type: Type of embedding encoder ("ollama")
        model: Model name (required for ollama)
        base_url: Server URL (required for ollama)
        timeout: Request timeout in seconds (default 30)

    Returns:
        Some(VectorEmbeddingEncoder) if creation succeeds, Nothing() if type unknown or params missing

    Note:
        Additional encoder types (OpenAI, Sentence Transformers) can be
        added here when implemented.
    """
    try:
        encoder_enum = EmbeddingEncoderType(encoder_type)
    except ValueError:
        return Nothing()

    if encoder_enum == EmbeddingEncoderType.OLLAMA:
        if model is None or base_url is None:
            return Nothing()
        return Some(
            OllamaVectorEmbeddingEncoder(
                model=model,
                base_url=base_url,
                timeout=timeout,
            )
        )

    return Nothing()
