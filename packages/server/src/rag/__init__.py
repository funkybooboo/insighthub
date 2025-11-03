"""
RAG System - Modular Retrieval-Augmented Generation

A playground for experimenting with different RAG algorithms, chunking strategies,
embeddings, and storage backends.

Quick Start:
    >>> from rag import create_rag
    >>> rag = create_rag(
    ...     rag_type="vector",
    ...     chunking_strategy="sentence",
    ...     embedding_type="ollama",
    ...     vector_store_type="qdrant"
    ... )

Architecture:
    - chunking: Text preprocessing strategies (character, sentence, word, semantic)
    - embeddings: Embedding models (Ollama, OpenAI, Sentence Transformers)
    - stores: Storage backends (vector: Qdrant/Pinecone, graph: future)
    - algorithms: RAG implementations (vector, graph)
"""

from src.rag.base import BaseRAG, RAGType
from src.rag.factory import create_rag, create_vector_rag
from src.rag.types import Chunk, Document, Metadata, SearchResult, Stats

__version__ = "0.1.0"

__all__ = [
    # Main factory
    "create_rag",
    "create_vector_rag",
    # Base classes
    "BaseRAG",
    "RAGType",
    # Types
    "Document",
    "Chunk",
    "Metadata",
    "SearchResult",
    "Stats",
]
