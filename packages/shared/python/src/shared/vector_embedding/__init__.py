"""Vector embedding for text representations."""

from shared.vector_embedding.encoder import EmbeddingEncoder
from shared.vector_embedding.ollama_embeddings import OllamaEmbeddings

__all__ = ["EmbeddingEncoder", "OllamaEmbeddings"]
