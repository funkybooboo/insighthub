"""Factory for creating status repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .sql_status_repository import SqlStatusRepository
from .status_repository import StatusRepository


def create_status_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[StatusRepository]:
    """
    Create a status repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        StatusRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlStatusRepository(db)
    return None
