"""Factory for creating document chunker instances."""

from enum import Enum

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
    def create_chunker(chunker_type: str, **kwargs) -> Chunker:
        """Create a chunker instance. Alias for create_chunker_from_config.

        Args:
            chunker_type: Type of chunker to create
            **kwargs: Additional configuration (chunk_size, overlap)

        Returns:
            Chunker instance

        Raises:
            ValueError: If chunker_type is not supported
        """
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
            "label": str(info["label"]),
            "description": str(info["description"]),
        }
        for key, info in AVAILABLE_CHUNKERS.items()
    ]


def create_chunker_from_config(
    chunking_algorithm: str,
    chunk_size: int,
    overlap: int,
) -> Chunker:
    """
    Create a document chunker instance based on algorithm configuration.

    Args:
        chunking_algorithm: Algorithm type ("sentence", "character", "semantic")
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        Chunker instance

    Raises:
        ValueError: If chunking_algorithm is not supported
    """
    chunker_info = AVAILABLE_CHUNKERS.get(chunking_algorithm)
    if chunker_info is None:
        available = list(AVAILABLE_CHUNKERS.keys())
        raise ValueError(
            f"Unsupported chunking algorithm: {chunking_algorithm}. "
            f"Available chunkers: {', '.join(available)}"
        )

    chunker_class = chunker_info["class"]
    if chunker_class == SentenceDocumentChunker:
        return SentenceDocumentChunker(chunk_size=chunk_size, overlap=overlap)
    elif chunker_class == CharacterDocumentChunker:
        return CharacterDocumentChunker(chunk_size=chunk_size, overlap=overlap)
    elif chunker_class == SemanticDocumentChunker:
        return SemanticDocumentChunker(chunk_size=chunk_size, overlap=overlap)
    else:
        raise ValueError(f"Unknown chunker class: {chunker_class}")
