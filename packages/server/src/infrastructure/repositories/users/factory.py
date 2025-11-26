"""Factory for creating users repository instances."""

from .in_memory_user_repository import InMemoryUserRepository
from .sql_user_repository import SqlUserRepository
from .user_repository import UserRepository


def create_user_repository(repo_type: str = "memory", db=None) -> UserRepository:
    """Create a users repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres", "sqlite")
        db: Pre-configured database instance (required for postgres/sqlite)

    Returns:
        UserRepository instance

    Raises:
        ValueError: If repo_type is not supported or db is missing for SQL repos
    """
    if repo_type == "in_memory":
        return InMemoryUserRepository()
    elif repo_type in ("postgres", "sqlite"):
        if db is None:
            raise ValueError("db is required for postgres/sqlite repository")
        return SqlUserRepository(db)
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
