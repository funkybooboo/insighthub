"""Base interface for entity extraction in Graph RAG.

This module defines the abstract interface for extracting entities from text
as part of the Graph RAG pipeline.
"""

from abc import ABC, abstractmethod

from src.infrastructure.types.graph import Entity


class EntityExtractor(ABC):
    """Abstract base class for entity extraction.

    Implementations should extract named entities from text and return them
    as Entity objects with proper EntityType enum values.
    """

    @abstractmethod
    def extract_entities(self, text: str) -> list[Entity]:
        """Extract entities from text.

        Args:
            text: Input text to extract entities from

        Returns:
            List of extracted entities with proper EntityType enums

        Note:
            Entity IDs should be deterministic based on normalized text
            to support deduplication across documents.
        """
        pass

    @abstractmethod
    def extract_entities_batch(self, texts: list[str]) -> list[list[Entity]]:
        """Extract entities from multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of entity lists, one per input text

        Note:
            Implementations may optimize batch processing for better performance.
        """
        pass
