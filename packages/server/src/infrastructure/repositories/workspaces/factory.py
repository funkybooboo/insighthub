"""Factory for creating workspace repository instances."""

from .in_memory_workspace_repository import InMemoryWorkspaceRepository
from .workspace_repository import WorkspaceRepository


def create_workspace_repository(repo_type: str = "memory") -> WorkspaceRepository:
    """Create a workspace repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")

    Returns:
        WorkspaceRepository instance

    Raises:
        ValueError: If repo_type is not supported
    """
    if repo_type == "memory":
        return InMemoryWorkspaceRepository()
    elif repo_type == "postgres":
        # TODO: Implement SQL repository
        raise NotImplementedError("PostgreSQL repository not yet implemented")
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
