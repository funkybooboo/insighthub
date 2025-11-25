"""Factory for creating community repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .community_repository import CommunityRepository
from .sql_community_repository import SqlCommunityRepository


def create_community_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[CommunityRepository]:
    """
    Create a community repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        CommunityRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlCommunityRepository(db)
    return None