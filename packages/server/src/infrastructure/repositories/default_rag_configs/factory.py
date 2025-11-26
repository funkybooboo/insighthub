"""Factory for creating default RAG config repository instances."""

from .default_rag_config_repository import DefaultRagConfigRepository
from .in_memory_default_rag_config_repository import InMemoryDefaultRagConfigRepository


def create_default_rag_config_repository(repo_type: str = "memory") -> DefaultRagConfigRepository:
    """Create a default RAG config repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")

    Returns:
        DefaultRagConfigRepository instance

    Raises:
        ValueError: If repo_type is not supported
    """
    if repo_type == "memory":
        return InMemoryDefaultRagConfigRepository()
    elif repo_type == "postgres":
        # TODO: Implement SQL repository
        raise NotImplementedError("PostgreSQL repository not yet implemented")
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
