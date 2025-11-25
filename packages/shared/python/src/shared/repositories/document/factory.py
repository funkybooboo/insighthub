"""Factory for creating document repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .document_repository import DocumentRepository
from .sql_document_repository import SqlDocumentRepository


def create_document_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[DocumentRepository]:
    """
    Create a document repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        DocumentRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlDocumentRepository(db)
    return None
