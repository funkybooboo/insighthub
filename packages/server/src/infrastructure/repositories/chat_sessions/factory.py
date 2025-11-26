"""Factory for creating chats session repository instances."""

from .chat_session_repository import ChatSessionRepository
from .in_memory_chat_session_repository import InMemoryChatSessionRepository
from .sql_chat_session_repository import SqlChatSessionRepository


def create_chat_session_repository(repo_type: str = "memory", db=None) -> ChatSessionRepository:
    """Create a chats session repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")
        db: Pre-configured database instance (required for postgres)

    Returns:
        ChatSessionRepository instance

    Raises:
        ValueError: If repo_type is not supported or db is missing for SQL repos
    """
    if repo_type == "memory":
        return InMemoryChatSessionRepository()
    elif repo_type == "postgres":
        if db is None:
            raise ValueError("db is required for postgres repository")
        return SqlChatSessionRepository(db)
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
