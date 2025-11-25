"""Factory for creating user repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .sql_user_repository import SqlUserRepository
from .user_repository import UserRepository


def create_user_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[UserRepository]:
    """
    Create a user repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        UserRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlUserRepository(db)
    return None
