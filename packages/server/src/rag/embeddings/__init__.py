"""
Embedding models module

Provides various embedding model implementations.
All models implement the EmbeddingModel interface.
"""

from src.rag.embeddings.base import EmbeddingModel
from src.rag.embeddings.dummy import DummyEmbeddings
from src.rag.embeddings.ollama import OllamaEmbeddings
from src.rag.embeddings.openai import OpenAIEmbeddings
from src.rag.embeddings.sentence_transformer import SentenceTransformerEmbeddings

__all__ = [
    "EmbeddingModel",
    "OllamaEmbeddings",
    "OpenAIEmbeddings",
    "SentenceTransformerEmbeddings",
    "DummyEmbeddings",
]
