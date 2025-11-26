"""Retrieval types for vector search and RAG operations."""

from dataclasses import dataclass

from src.infrastructure.types.common import MetadataDict


@dataclass
class RetrievalResult:
    """
    Result from a vector similarity search operation.

    Represents a single retrieved item with its similarity score and metadata.
    This is an intermediate result used internally by vector stores before
    being processed into QueryResult objects for the final RAG response.
    """

    id: str
    score: float
    source: str
    payload: MetadataDict