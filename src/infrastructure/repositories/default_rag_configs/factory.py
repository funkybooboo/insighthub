"""Factory for creating default RAG config repository instances."""

from .default_rag_config_repository import DefaultRagConfigRepository
from .in_memory_default_rag_config_repository import InMemoryDefaultRagConfigRepository
from .sql_default_rag_config_repository import SqlDefaultRagConfigRepository


def create_default_rag_config_repository(
    repo_type: str = "memory", db=None
) -> DefaultRagConfigRepository:
    """Create a default RAG config repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")
        db: Pre-configured database instance (required for postgres)

    Returns:
        DefaultRagConfigRepository instance

    Raises:
        ValueError: If repo_type is not supported or db is missing for SQL repos
    """
    if repo_type == "in_memory":
        return InMemoryDefaultRagConfigRepository()
    elif repo_type == "postgres":
        if db is None:
            raise ValueError("db is required for postgres repository")
        return SqlDefaultRagConfigRepository(db)
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
