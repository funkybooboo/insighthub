"""
Document chunking module

Provides various strategies for splitting documents into chunks.
Use the factory function for easy instantiation:

    from src.rag.chunking import get_chunker
    chunker = get_chunker("sentence", chunk_size=500, chunk_overlap=50)
"""

from src.rag.chunking.base import BaseChunker, ChunkingStrategy
from src.rag.chunking.factory import get_chunker, list_chunking_strategies
from src.rag.chunking.text_chunkers import (
    CharacterChunker,
    SemanticChunker,
    SentenceChunker,
    WordChunker,
)

__all__ = [
    # Base classes and enums
    "BaseChunker",
    "ChunkingStrategy",
    # Implementations
    "CharacterChunker",
    "SentenceChunker",
    "WordChunker",
    "SemanticChunker",
    # Factory
    "get_chunker",
    "list_chunking_strategies",
]
