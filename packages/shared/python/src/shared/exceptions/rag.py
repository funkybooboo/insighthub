"""Exceptions specific to the RAG module."""

from shared.exceptions.base import DomainException


class RagException(DomainException):
    """Base exception for all RAG-related errors."""

    def __init__(self, message: str, status_code: int = 500):
        """Initialize RAG exception."""
        super().__init__(f"RAG Error: {message}", status_code)


class RagChunkingError(RagException):
    """Raised when document chunking fails."""

    def __init__(self, document_id: str, message: str):
        """Initialize chunking error."""
        super().__init__(f"Failed to chunk document {document_id}: {message}", status_code=500)


class RagEmbeddingError(RagException):
    """Raised when embedding generation fails."""

    def __init__(self, message: str):
        """Initialize embedding error."""
        super().__init__(f"Failed to generate embeddings: {message}", status_code=500)


class RagVectorStoreError(RagException):
    """Raised for errors related to the vector store."""

    def __init__(self, message: str):
        """Initialize vector store error."""
        super().__init__(f"Vector store operation failed: {message}", status_code=500)


class RagGraphStoreError(RagException):
    """Raised for errors related to the graph store."""

    def __init__(self, message: str):
        """Initialize graph store error."""
        super().__init__(f"Graph store operation failed: {message}", status_code=500)
