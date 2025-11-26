"""Factory for creating chats message repository instances."""

from .chat_message_repository import ChatMessageRepository
from .in_memory_chat_message_repository import InMemoryChatMessageRepository


def create_chat_message_repository(repo_type: str = "memory") -> ChatMessageRepository:
    """Create a chats message repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")

    Returns:
        ChatMessageRepository instance

    Raises:
        ValueError: If repo_type is not supported
    """
    if repo_type == "memory":
        return InMemoryChatMessageRepository()
    elif repo_type == "postgres":
        # TODO: Implement SQL repository
        raise NotImplementedError("PostgreSQL repository not yet implemented")
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")
