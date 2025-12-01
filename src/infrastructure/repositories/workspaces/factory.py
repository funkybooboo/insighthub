"""Factory for creating workspace repository instances."""

from .in_memory_workspace_repository import InMemoryWorkspaceRepository
from .sql_workspace_repository import SqlWorkspaceRepository
from .workspace_repository import WorkspaceRepository


def create_workspace_repository(repo_type: str = "memory", db=None) -> WorkspaceRepository:
    """Create a workspace repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")
        db: Pre-configured database instance (required for postgres)

    Returns:
        WorkspaceRepository instance

    Raises:
        ValueError: If repo_type is not supported or db is missing for SQL repos
    """
    if repo_type == "in_memory":
        return InMemoryWorkspaceRepository()
    elif repo_type == "postgres":
        if db is None:
            raise ValueError("db is required for postgres repository")
        return SqlWorkspaceRepository(db)
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
