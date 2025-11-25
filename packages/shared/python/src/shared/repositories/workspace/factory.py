"""Factory for creating workspace repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .sql_workspace_repository import SqlWorkspaceRepository
from .workspace_repository import WorkspaceRepository


def create_workspace_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[WorkspaceRepository]:
    """
    Create a workspace repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        WorkspaceRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlWorkspaceRepository(db)
    return None
