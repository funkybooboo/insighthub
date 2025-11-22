"""Vector embedding for text representations."""

from shared.vector_embedding_encoder.vector_embedding_encoder import (
    EmbeddingError,
    VectorEmbeddingEncoder,
)
from shared.vector_embedding_encoder.ollama_vector_embedding_encoder import (
    OllamaVectorEmbeddingEncoder,
)

__all__ = [
    "EmbeddingError",
    "VectorEmbeddingEncoder",
    "OllamaVectorEmbeddingEncoder",
]
