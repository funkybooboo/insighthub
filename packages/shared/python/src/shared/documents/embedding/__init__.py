"""Vector embedding for text representations."""

from shared.documents.embedding.ollama_vector_embedding_encoder import OllamaVectorEmbeddingEncoder
from shared.documents.embedding.vector_embedding_encoder import (
    EmbeddingError,
    VectorEmbeddingEncoder,
)

__all__ = [
    "EmbeddingError",
    "VectorEmbeddingEncoder",
    "OllamaVectorEmbeddingEncoder",
]
