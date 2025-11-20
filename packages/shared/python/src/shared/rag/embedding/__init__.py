"""Embedding components."""

from .interface import EmbeddingEncoder
from .ollama_embeddings import OllamaEmbeddings

__all__ = ["EmbeddingEncoder", "OllamaEmbeddings"]
