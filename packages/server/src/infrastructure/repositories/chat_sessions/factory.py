"""Factory for creating chats session repository instances."""

from .in_memory_chat_session_repository import InMemoryChatSessionRepository
from .chat_session_repository import ChatSessionRepository


def create_chat_session_repository(repo_type: str = "memory") -> ChatSessionRepository:
    """Create a chats session repository instance based on configuration.

    Args:
        repo_type: Type of repository ("memory", "postgres")

    Returns:
        ChatSessionRepository instance

    Raises:
        ValueError: If repo_type is not supported
    """
    if repo_type == "memory":
        return InMemoryChatSessionRepository()
    elif repo_type == "postgres":
        # TODO: Implement SQL repository
        raise NotImplementedError("PostgreSQL repository not yet implemented")
    else:
        raise ValueError(f"Unsupported repository type: {repo_type}")