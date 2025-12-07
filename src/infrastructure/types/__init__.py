"""Shared types used across the application."""

from returns.result import Failure, Result, Success

from src.infrastructure.types.common import (
    FilterDict,
    HealthStatus,
    MetadataDict,
    PrimitiveValue,
    ResultHandler,
)
from src.infrastructure.types.document import Chunk, Document
from src.infrastructure.types.errors import (
    DatabaseError,
    DocumentProcessingError,
    DocumentUploadError,
    LlmProviderError,
    NotFoundError,
    StorageError,
    ValidationError,
    VectorStoreError,
    WorkflowError,
)
from src.infrastructure.types.pagination import PaginatedResult, Pagination, PaginationError
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
    "ResultHandler",
    "Document",
    "Chunk",
    "RagSystem",
    "QueryResult",
    "ChunkData",
    "RetrievalResult",
    "Pagination",
    "PaginatedResult",
    "PaginationError",
    "ValidationError",
    "NotFoundError",
    "WorkflowError",
    "DatabaseError",
    "StorageError",
    "VectorStoreError",
    "LlmProviderError",
    "DocumentUploadError",
    "DocumentProcessingError",
]
