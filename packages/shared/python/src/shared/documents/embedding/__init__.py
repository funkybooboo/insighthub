"""Vector embedding for text representations."""

from shared.documents.embedding.vector_embedding_encoder import (
    EmbeddingError,
    VectorEmbeddingEncoder,
)
from shared.documents.embedding.ollama_vector_embedding_encoder import (
    OllamaVectorEmbeddingEncoder,
)

__all__ = [
    "EmbeddingError",
    "VectorEmbeddingEncoder",
    "OllamaVectorEmbeddingEncoder",
]
