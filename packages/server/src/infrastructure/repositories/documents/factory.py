"""Factory for creating document repository instances."""

from .document_repository import DocumentRepository
from .in_memory_document_repository import InMemoryDocumentRepository
from .sql_document_repository import SqlDocumentRepository


def create_document_repository(repo_type: str = "memory", db=None) -> DocumentRepository:
    """Create a document repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")
        db: Pre-configured database instance (required for postgres)

    Returns:
        DocumentRepository instance

    Raises:
        ValueError: If repo_type is not supported or db is missing for SQL repos
    """
    if repo_type == "memory":
        return InMemoryDocumentRepository()
    elif repo_type == "postgres":
        if db is None:
            raise ValueError("db is required for postgres repository")
        return SqlDocumentRepository(db)
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
