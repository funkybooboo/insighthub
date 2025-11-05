"""Factory for creating repository instances."""

from sqlalchemy.orm import Session

from .interfaces import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    UserRepository,
)
from .repository import (
    SqlChatMessageRepository,
    SqlChatSessionRepository,
    SqlDocumentRepository,
    SqlUserRepository,
)


def create_user_repository(db: Session) -> UserRepository:
    """
    Create a UserRepository instance.

    Args:
        db: Database session

    Returns:
        UserRepository: Repository instance
    """
    return SqlUserRepository(db)


def create_document_repository(db: Session) -> DocumentRepository:
    """
    Create a DocumentRepository instance.

    Args:
        db: Database session

    Returns:
        DocumentRepository: Repository instance
    """
    return SqlDocumentRepository(db)


def create_chat_session_repository(db: Session) -> ChatSessionRepository:
    """
    Create a ChatSessionRepository instance.

    Args:
        db: Database session

    Returns:
        ChatSessionRepository: Repository instance
    """
    return SqlChatSessionRepository(db)


def create_chat_message_repository(db: Session) -> ChatMessageRepository:
    """
    Create a ChatMessageRepository instance.

    Args:
        db: Database session

    Returns:
        ChatMessageRepository: Repository instance
    """
    return SqlChatMessageRepository(db)
