"""Factory for creating document chunker instances."""

from enum import Enum
from typing import Optional

from .document_chunker import Chunker
from .sentence_document_chunker import SentenceDocumentChunker


class ChunkerType(Enum):
    """Enum for chunker implementation types."""

    SENTENCE = "sentence"


def create_chunker(
    chunker_type: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> Optional[Chunker]:
    """
    Create a document chunker instance based on configuration.

    Args:
        chunker_type: Type of chunker ("sentence")
        chunk_size: Target size of each chunk in characters (required)
        overlap: Number of characters to overlap between chunks (required)

    Returns:
        Chunker if creation succeeds, None if type unknown or params missing

    Note:
        Additional chunker types (character, paragraph, semantic) can be
        added here when implemented.
    """
    try:
        chunker_enum = ChunkerType(chunker_type)
    except ValueError:
        return None

    if chunker_enum == ChunkerType.SENTENCE:
        if chunk_size is None or overlap is None:
            return None
        return SentenceDocumentChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )

    return None
