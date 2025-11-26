"""Factory for creating document repository instances."""

from .document_repository import DocumentRepository
from .in_memory_document_repository import InMemoryDocumentRepository


def create_document_repository(repo_type: str = "memory") -> DocumentRepository:
    """Create a document repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")

    Returns:
        DocumentRepository instance

    Raises:
        ValueError: If repo_type is not supported
    """
    if repo_type == "memory":
        return InMemoryDocumentRepository()
    elif repo_type == "postgres":
        # TODO: Implement SQL repository
        raise NotImplementedError("PostgreSQL repository not yet implemented")
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
