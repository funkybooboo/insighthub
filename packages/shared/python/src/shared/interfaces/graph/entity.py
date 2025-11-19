"""Entity extraction interface for Graph RAG."""

from abc import ABC, abstractmethod

from shared.types import Chunk, GraphNode


class EntityExtractor(ABC):
    """
    Extracts named entities from text chunks using NER or LLM-based extraction.

    Implementations may use:
    - spaCy NER
    - LLM-based extraction (GPT, Claude, Llama)
    - Custom entity recognition models
    """

    @abstractmethod
    def extract_entities(self, chunk: Chunk) -> list[GraphNode]:
        """
        Extract entities from a text chunk.

        Args:
            chunk: Text chunk to extract entities from

        Returns:
            List of GraphNode objects representing extracted entities
        """
        raise NotImplementedError

    @abstractmethod
    def extract_entities_batch(self, chunks: list[Chunk]) -> list[list[GraphNode]]:
        """
        Batch extract entities from multiple chunks.

        Args:
            chunks: List of chunks to process

        Returns:
            List of entity lists (one per chunk)
        """
        raise NotImplementedError
