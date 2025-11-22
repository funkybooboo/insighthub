"""RAG configuration and result types."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from shared.types.common import PrimitiveValue


@dataclass
class ChunkerConfig:
    """
    Configuration for text chunking.

    Attributes:
        strategy: Chunking strategy ('character', 'sentence', 'word', 'semantic')
        chunk_size: Target size of each chunk
        overlap: Overlap between consecutive chunks
        min_chunk_size: Minimum allowed chunk size
    """

    strategy: str
    chunk_size: int
    overlap: int = 0
    min_chunk_size: int = 50


@dataclass
class RagConfig:
    """
    Canonical RAG configuration used across server/shared.

    This model represents both the DB-persistent configuration and runtime
    configuration needed by the RAG pipelines.
    """

    id: Optional[str] = None
    workspace_id: str = ""
    rag_type: str = "vector"  # 'vector', 'graph', or 'hybrid'
    chunking_strategy: str = "sentence"
    embedding_model: str = "nomic-embed-text"
    embedding_dim: Optional[int] = None
    retriever_type: str = "vector"  # e.g., 'vector' or 'graph'
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 8
    rerank_enabled: bool = False
    rerank_model: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """
    Result from RAG retrieval.

    Attributes:
        content: Retrieved text content
        score: Relevance score
        metadata: Associated metadata
        document_id: Source document ID
        chunk_id: Chunk identifier
    """

    content: str
    score: float
    metadata: Dict[str, PrimitiveValue]
    document_id: str
    chunk_id: str
