"""Factory for creating users repository instances."""

from src.infrastructure.database import create_database

from .sql_user_repository import SqlUserRepository
from .user_repository import UserRepository


def create_user_repository(
    db_type: str = "sqlite", db_url: str = "sqlite:///insighthub.db"
) -> UserRepository:
    """Create a users repository instance based on configuration.

    Args:
        db_type: Type of database ("postgres", "sqlite", etc.)
        db_url: Database connection URL

    Returns:
        UserRepository instance

    Raises:
        ValueError: If db_type is not supported
    """
    if db_type == "postgres":
        # For now, return None as we don't have a full Postgres implementation
        # In a real implementation, this would create a PostgresUserRepository
        raise NotImplementedError("PostgreSQL repository not yet implemented")
    elif db_type == "sqlite":
        # Create SQLite database connection
        db = create_database(db_url)
        return SqlUserRepository(db)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
