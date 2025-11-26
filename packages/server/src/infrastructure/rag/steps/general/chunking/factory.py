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


class ChunkerFactory:
    """Factory class for creating chunkers."""

    @staticmethod
    def create_chunker(chunker_type: str, **kwargs) -> Optional[Chunker]:
        """Create a chunker instance. Alias for create_chunker_from_config."""
        chunk_size = kwargs.get("chunk_size", 500)
        overlap = kwargs.get("overlap", 50)
        return create_chunker_from_config(chunker_type, chunk_size, overlap)


AVAILABLE_CHUNKERS = {
    "sentence": {
        "class": SentenceDocumentChunker,
        "label": "Sentence",
        "description": "Split by sentence boundaries",
    },
    "character": {
        "class": CharacterDocumentChunker,
        "label": "Character",
        "description": "Fixed character size chunks",
    },
    "semantic": {
        "class": SemanticDocumentChunker,
        "label": "Semantic",
        "description": "Semantically coherent chunks",
    },
}


def get_available_chunkers() -> list[dict[str, str]]:
    """Get list of available chunking algorithms."""
    return [
        {
            "value": key,
            "label": info["label"],
            "description": info["description"],
        }
        for key, info in AVAILABLE_CHUNKERS.items()
    ]


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
    chunker_info = AVAILABLE_CHUNKERS.get(chunking_algorithm)
    if chunker_info is None:
        return None

    return chunker_info["class"](
        chunk_size=chunk_size,
        overlap=overlap,
    )
