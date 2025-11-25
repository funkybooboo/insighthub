"""Factory for creating chat session repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .chat_session_repository import ChatSessionRepository
from .sql_chat_session_repository import SqlChatSessionRepository


def create_chat_session_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[ChatSessionRepository]:
    """
    Create a chat session repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        ChatSessionRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlChatSessionRepository(db)
    return None
