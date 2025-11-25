"""Factory for creating entity repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .entity_repository import EntityRepository
from .sql_entity_repository import SqlEntityRepository


def create_entity_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[EntityRepository]:
    """
    Create an entity repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        EntityRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlEntityRepository(db)
    return None