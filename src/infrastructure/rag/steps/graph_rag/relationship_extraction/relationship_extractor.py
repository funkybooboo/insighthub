"""Base interface for relationship extraction in Graph RAG.

This module defines the abstract interface for extracting relationships between
entities as part of the Graph RAG pipeline.
"""

from abc import ABC, abstractmethod

from src.infrastructure.types.graph import Entity, Relationship


class RelationshipExtractor(ABC):
    """Abstract base class for relationship extraction.

    Implementations should extract relationships between entities from text
    and return them as Relationship objects with proper RelationType enum values.
    """

    @abstractmethod
    def extract_relationships(self, text: str, entities: list[Entity]) -> list[Relationship]:
        """Extract relationships between entities.

        Args:
            text: Input text containing the entities
            entities: Entities found in the text

        Returns:
            List of relationships with proper RelationType enums

        Note:
            Relationship IDs should be deterministic based on source entity,
            target entity, and relation type.
        """
        pass

    @abstractmethod
    def extract_relationships_batch(
        self, texts: list[str], entities_batch: list[list[Entity]]
    ) -> list[list[Relationship]]:
        """Extract relationships from multiple texts.

        Args:
            texts: List of input texts
            entities_batch: List of entity lists, one per input text

        Returns:
            List of relationship lists, one per input text

        Note:
            Implementations may optimize batch processing for better performance.
        """
        pass
