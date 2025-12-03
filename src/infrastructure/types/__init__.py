"""Shared types used across the application."""

from returns.result import Failure, Result, Success

from src.infrastructure.types.common import FilterDict, HealthStatus, MetadataDict, PrimitiveValue
from src.infrastructure.types.document import Chunk, Document
from src.infrastructure.types.errors import (
    DatabaseError,
    NotFoundError,
    StorageError,
    ValidationError,
    VectorStoreError,
    WorkflowError,
)
from src.infrastructure.types.rag import ChunkData, QueryResult, RagSystem
from src.infrastructure.types.retrieval import RetrievalResult

__all__ = [
    "Success",
    "Failure",
    "Result",
    "MetadataDict",
    "FilterDict",
    "PrimitiveValue",
    "HealthStatus",
    "Document",
    "Chunk",
    "RagSystem",
    "QueryResult",
    "ChunkData",
    "RetrievalResult",
    "ValidationError",
    "NotFoundError",
    "WorkflowError",
    "DatabaseError",
    "StorageError",
    "VectorStoreError",
]
