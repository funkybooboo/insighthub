"""Factory for creating chunk repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .chunk_repository import ChunkRepository
from .sql_chunk_repository import SqlChunkRepository


def create_chunk_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[ChunkRepository]:
    """
    Create a chunk repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        ChunkRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlChunkRepository(db)
    return None