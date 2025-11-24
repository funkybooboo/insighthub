"""Exception types and DTOs for error handling."""

from .base import (
    AlreadyExistsError,
    ConflictError,
    DomainException,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from .dtos import ErrorResponse
from .llm import LlmException, LlmGenerationError, LlmProviderError
from .rag import (
    RagChunkingError,
    RagEmbeddingError,
    RagException,
    RagGraphStoreError,
    RagVectorStoreError,
)
from .storage import BlobStorageError, FileSystemError, StorageException

__all__ = [
    "AlreadyExistsError",
    "ConflictError",
    "DomainException",
    "ErrorResponse",
    "ForbiddenError",
    "NotFoundError",
    "UnauthorizedError",
    "ValidationError",
    "LlmException",
    "LlmGenerationError",
    "LlmProviderError",
    "RagException",
    "RagChunkingError",
    "RagEmbeddingError",
    "RagVectorStoreError",
    "RagGraphStoreError",
    "StorageException",
    "BlobStorageError",
    "FileSystemError",
]
