"""
Strict and refined type definitions for the RAG system.
"""

from typing import Literal, TypedDict

PrimitiveValue = str | int | float | bool


MetadataValue = (
    PrimitiveValue | list[PrimitiveValue] | list[list[PrimitiveValue]] | dict[str, PrimitiveValue]
)


class Document(TypedDict, total=False):
    text: str
    metadata: dict[str, MetadataValue]


class Chunk(TypedDict, total=False):
    """
    Represents a chunk of a document.
    """

    id: str | None  # Optional unique ID for the chunk
    text: str
    metadata: dict[str, MetadataValue]


class SearchResult(TypedDict):
    id: str
    score: float
    metadata: dict[str, MetadataValue]


class RetrievalResult(TypedDict):
    id: str
    text: str
    score: float
    metadata: dict[str, MetadataValue]


class QueryResult(TypedDict, total=False):
    query: str
    chunks: list[RetrievalResult]
    answer: str
    stats: dict[str, MetadataValue]


class ChunkerConfig(TypedDict, total=False):
    strategy: str
    chunk_size: int
    chunk_overlap: int
    extra_options: dict[str, MetadataValue] | None  # For strategy-specific parameters


class RagStats(TypedDict):
    total_chunks: int
    embedding_dimension: int
    chunking_strategy: str
    embedding_model: str
    vector_store: str


class RagConfig(TypedDict, total=False):
    rag_type: Literal["vector", "graph"] | str
    chunking_strategy: Literal["character", "sentence", "word"] | str
    embedding_type: Literal["ollama", "openai", "sentence_transformer", "dummy"] | str
    vector_store_type: Literal["qdrant", "pinecone", "in_memory"] | str
    chunk_size: int
    chunk_overlap: int
    embedding_model_name: str
    vector_store_host: str
    vector_store_port: int
    collection_name: str
