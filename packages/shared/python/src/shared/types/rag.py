"""RAG configuration and result types."""

from dataclasses import dataclass
from typing import Any

from shared.types.common import PrimitiveValue


@dataclass
class ChunkerConfig:
    """
    Configuration for a chunking strategy.

    Attributes:
        strategy: Chunking method (e.g., 'sentence', 'character', 'word')
        chunk_size: Target size for chunks
        overlap: Overlap between consecutive chunks
        extra_options: Additional strategy-specific options
    """

    strategy: str
    chunk_size: int
    overlap: int
    extra_options: dict[str, Any] | None = None


@dataclass
class RagConfig:
    """
    Configuration parameters for a RAG workspace or instance.

    Attributes:
        workspace_id: Workspace or tenant identifier
        rag_type: RAG type ('vector', 'graph', 'hybrid')
        chunking_strategy: Chunking method
        embedding_model: Name of the embedding model to use
        embedding_dim: Dimensionality of the embedding vectors
        top_k: Default number of results to retrieve for queries
    """

    workspace_id: str
    rag_type: str
    chunking_strategy: str
    embedding_model: str
    embedding_dim: int
    top_k: int = 8


@dataclass
class SearchResult:
    """
    Result from vector or graph search.

    Attributes:
        id: Identifier of the retrieved chunk/node
        score: Similarity score (higher is better)
        metadata: Associated metadata
        payload: Content payload (text, properties, etc.)
    """

    id: str
    score: float
    metadata: dict[str, PrimitiveValue]
    payload: dict[str, Any] | None = None
