"""Type definitions for RAG system."""

from typing import TypedDict, Literal


class Document(TypedDict, total=False):
    """Input document structure."""

    text: str  # Required
    metadata: dict[str, str | int | float | bool]  # Optional


class Chunk(TypedDict):
    """Chunked document with metadata."""

    text: str
    metadata: dict[str, str | int | float | bool]


class SearchResult(TypedDict):
    """Vector store search result."""

    id: str
    score: float
    metadata: dict[str, str | int | float | bool]


class RetrievalResult(TypedDict):
    """RAG retrieval result with chunk content."""

    id: str
    text: str
    score: float
    metadata: dict[str, str | int | float | bool]


class QueryResult(TypedDict, total=False):
    """Complete RAG query result."""

    query: str
    chunks: list[RetrievalResult]
    answer: str  # Optional, only if generate_answer=True
    stats: dict[str, int | float | str]


class ChunkerConfig(TypedDict):
    """Chunker configuration."""

    strategy: str
    chunk_size: int
    chunk_overlap: int


class RagStats(TypedDict):
    """RAG system statistics."""

    total_chunks: int
    embedding_dimension: int
    chunking_strategy: str
    embedding_model: str
    vector_store: str


class RagConfig(TypedDict, total=False):
    """Configuration for creating RAG instances via factory."""

    rag_type: Literal["vector", "graph"]
    chunking_strategy: Literal["character", "sentence", "word"]
    embedding_type: Literal["ollama", "openai", "sentence_transformer", "dummy"]
    vector_store_type: Literal["qdrant", "pinecone", "in_memory"]
    chunk_size: int
    chunk_overlap: int
    embedding_model_name: str
    vector_store_host: str
    vector_store_port: int
    collection_name: str
