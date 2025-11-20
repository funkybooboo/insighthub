"""Graph RAG interfaces for entity and relationship extraction."""

from abc import ABC, abstractmethod
from typing import Any, List

from shared.types.document import Chunk
from shared.types.graph import GraphNode


class EntityExtractor(ABC):
    """
    Interface for extracting named entities from text chunks.
    
    Implementations can use:
    - spaCy NER
    - LLM-based extraction
    - Custom entity recognition models
    """

    @abstractmethod
    def extract_entities(self, chunk: Chunk) -> List[GraphNode]:
        """
        Extract entities from a text chunk.

        Args:
            chunk: Text chunk to extract entities from

        Returns:
            List[GraphNode]: List of extracted entities

        Raises:
            EntityExtractionError: If extraction fails
        """
        pass

    @abstractmethod
    def extract_entities_batch(self, chunks: List[Chunk]) -> List[List[GraphNode]]:
        """
        Batch extract entities from multiple chunks.

        Args:
            chunks: List of chunks to process

        Returns:
            List[List[GraphNode]]: List of entity lists (one per chunk)

        Raises:
            EntityExtractionError: If extraction fails
        """
        pass