"""Factory for creating chats message repository instances."""

from .chat_message_repository import ChatMessageRepository
from .in_memory_chat_message_repository import InMemoryChatMessageRepository
from .sql_chat_message_repository import SqlChatMessageRepository


def create_chat_message_repository(repo_type: str = "memory", db=None) -> ChatMessageRepository:
    """Create a chats message repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")
        db: Pre-configured database instance (required for postgres)

    Returns:
        ChatMessageRepository instance

    Raises:
        ValueError: If repo_type is not supported or db is missing for SQL repos
    """
    if repo_type == "in_memory":
        return InMemoryChatMessageRepository()
    elif repo_type == "postgres":
        if db is None:
            raise ValueError("db is required for postgres repository")
        return SqlChatMessageRepository(db)
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
