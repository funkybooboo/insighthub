"""Factory for creating relationship repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .relationship_repository import RelationshipRepository
from .sql_relationship_repository import SqlRelationshipRepository


def create_relationship_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[RelationshipRepository]:
    """
    Create a relationship repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        RelationshipRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlRelationshipRepository(db)
    return None