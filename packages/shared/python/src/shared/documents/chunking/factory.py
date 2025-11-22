"""Factory for creating document chunker instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

from .document_chunker import Chunker
from .sentence_document_chunker import SentenceDocumentChunker


class ChunkerType(Enum):
    """Enum for chunker implementation types."""

    SENTENCE = "sentence"


def create_chunker(
    chunker_type: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> Option[Chunker]:
    """
    Create a document chunker instance based on configuration.

    Args:
        chunker_type: Type of chunker ("sentence")
        chunk_size: Target size of each chunk in characters (required)
        overlap: Number of characters to overlap between chunks (required)

    Returns:
        Some(Chunker) if creation succeeds, Nothing() if type unknown or params missing

    Note:
        Additional chunker types (character, paragraph, semantic) can be
        added here when implemented.
    """
    try:
        chunker_enum = ChunkerType(chunker_type)
    except ValueError:
        return Nothing()

    if chunker_enum == ChunkerType.SENTENCE:
        if chunk_size is None or overlap is None:
            return Nothing()
        return Some(
            SentenceDocumentChunker(
                chunk_size=chunk_size,
                overlap=overlap,
            )
        )

    return Nothing()
