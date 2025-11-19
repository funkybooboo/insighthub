"""Relation extraction interface for Graph RAG."""

from abc import ABC, abstractmethod

from shared.types import Chunk, GraphEdge, GraphNode


class RelationExtractor(ABC):
    """
    Extracts relationships between entities from text.

    Implementations may use:
    - Dependency parsing
    - LLM-based relation extraction
    - Pattern matching
    """

    @abstractmethod
    def extract_relations(
        self, chunk: Chunk, entities: list[GraphNode]
    ) -> list[GraphEdge]:
        """
        Extract relationships between entities in a chunk.

        Args:
            chunk: Text chunk containing entities
            entities: Entities extracted from the chunk

        Returns:
            List of GraphEdge objects representing relationships
        """
        raise NotImplementedError

    @abstractmethod
    def extract_relations_batch(
        self, chunks: list[Chunk], entities_per_chunk: list[list[GraphNode]]
    ) -> list[list[GraphEdge]]:
        """
        Batch extract relations from multiple chunks.

        Args:
            chunks: List of chunks to process
            entities_per_chunk: Entities for each chunk

        Returns:
            List of edge lists (one per chunk)
        """
        raise NotImplementedError
