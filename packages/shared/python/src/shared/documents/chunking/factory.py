"""Factory for creating document chunker instances."""

from enum import Enum
from typing import Optional

from .character_document_chunker import CharacterDocumentChunker
from .document_chunker import Chunker
from .semantic_document_chunker import SemanticDocumentChunker
from .sentence_document_chunker import SentenceDocumentChunker


class ChunkerType(Enum):
    """Enum for chunker implementation types."""

    SENTENCE = "sentence"


def create_chunker_from_config(
    chunking_algorithm: str,
    chunk_size: int,
    overlap: int,
) -> Optional[Chunker]:
    """
    Create a document chunker instance based on algorithm configuration.

    Args:
        chunking_algorithm: Algorithm type ("sentence", "character", "semantic")
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        Chunker if creation succeeds, None if algorithm unknown
    """
    if chunking_algorithm == "sentence":
        return SentenceDocumentChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )
    elif chunking_algorithm == "character":
        return CharacterDocumentChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )
    elif chunking_algorithm == "semantic":
        return SemanticDocumentChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )

    return None
