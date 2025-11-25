"""Factory for creating chat message repository instances."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase

from .chat_message_repository import ChatMessageRepository
from .sql_chat_message_repository import SqlChatMessageRepository


def create_chat_message_repository(
    repo_type: str,
    **kwargs: str,
) -> Optional[ChatMessageRepository]:
    """
    Create a chat message repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "postgres")
        **kwargs: Repository-specific configuration

    Returns:
        ChatMessageRepository if creation succeeds, None if type unknown
    """
    if repo_type == "postgres":
        db_url = kwargs.get("db_url")
        if not db_url:
            raise ValueError("db_url is required for postgres repository")
        db = PostgresSqlDatabase(db_url)
        return SqlChatMessageRepository(db)
    return None
