"""Factory for creating chat message repository instances.

Note: Concrete implementations (SQLAlchemy, etc.) should be registered here
when available. The shared library defines interfaces; implementations
typically live in the server package.
"""

from shared.types.option import Nothing, Option

from .chat_message_repository import ChatMessageRepository


def create_chat_message_repository(
    repo_type: str,
    **kwargs: str,
) -> Option[ChatMessageRepository]:
    """
    Create a chat message repository instance based on configuration.

    Args:
        repo_type: Type of repository (e.g., "sqlalchemy")
        **kwargs: Repository-specific configuration

    Returns:
        Some(ChatMessageRepository) if creation succeeds, Nothing() if type unknown

    Note:
        Register concrete implementations here when available.
        Example:
            if repo_type == "sqlalchemy":
                session = kwargs.get("session")
                return Some(SQLAlchemyChatMessageRepository(session))
    """
    # No implementations registered in shared library
    # Concrete implementations should be added when available
    return Nothing()
