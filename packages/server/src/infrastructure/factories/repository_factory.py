"""Factory for creating repository instances."""

from enum import Enum

from sqlalchemy.orm import Session

from src import config
from src.domains.chat.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    SqlChatMessageRepository,
    SqlChatSessionRepository,
)
from src.domains.documents.repositories import DocumentRepository, SqlDocumentRepository
from src.domains.users.repositories import SqlUserRepository, UserRepository


class UserRepositoryType(Enum):
    """Enum for user repository implementation types."""

    SQL = "sql"


class DocumentRepositoryType(Enum):
    """Enum for document repository implementation types."""

    SQL = "sql"


class ChatSessionRepositoryType(Enum):
    """Enum for chat session repository implementation types."""

    SQL = "sql"


class ChatMessageRepositoryType(Enum):
    """Enum for chat message repository implementation types."""

    SQL = "sql"


def create_user_repository(
    db: Session, repository_type: UserRepositoryType | None = None
) -> UserRepository:
    """
    Create a UserRepository instance.

    Args:
        db: Database session
        repository_type: Type of repository implementation to use.
                        If None, reads from config.USER_REPOSITORY_TYPE.

    Returns:
        UserRepository: Repository instance

    Raises:
        ValueError: If repository_type is not supported
    """
    if repository_type is None:
        repository_type = UserRepositoryType(config.USER_REPOSITORY_TYPE)

    if repository_type == UserRepositoryType.SQL:
        return SqlUserRepository(db)
    else:
        raise ValueError(f"Unsupported user repository type: {repository_type}")


def create_document_repository(
    db: Session, repository_type: DocumentRepositoryType | None = None
) -> DocumentRepository:
    """
    Create a DocumentRepository instance.

    Args:
        db: Database session
        repository_type: Type of repository implementation to use.
                        If None, reads from config.DOCUMENT_REPOSITORY_TYPE.

    Returns:
        DocumentRepository: Repository instance

    Raises:
        ValueError: If repository_type is not supported
    """
    if repository_type is None:
        repository_type = DocumentRepositoryType(config.DOCUMENT_REPOSITORY_TYPE)

    if repository_type == DocumentRepositoryType.SQL:
        return SqlDocumentRepository(db)
    else:
        raise ValueError(f"Unsupported document repository type: {repository_type}")


def create_chat_session_repository(
    db: Session, repository_type: ChatSessionRepositoryType | None = None
) -> ChatSessionRepository:
    """
    Create a ChatSessionRepository instance.

    Args:
        db: Database session
        repository_type: Type of repository implementation to use.
                        If None, reads from config.CHAT_SESSION_REPOSITORY_TYPE.

    Returns:
        ChatSessionRepository: Repository instance

    Raises:
        ValueError: If repository_type is not supported
    """
    if repository_type is None:
        repository_type = ChatSessionRepositoryType(config.CHAT_SESSION_REPOSITORY_TYPE)

    if repository_type == ChatSessionRepositoryType.SQL:
        return SqlChatSessionRepository(db)
    else:
        raise ValueError(f"Unsupported chat session repository type: {repository_type}")


def create_chat_message_repository(
    db: Session, repository_type: ChatMessageRepositoryType | None = None
) -> ChatMessageRepository:
    """
    Create a ChatMessageRepository instance.

    Args:
        db: Database session
        repository_type: Type of repository implementation to use.
                        If None, reads from config.CHAT_MESSAGE_REPOSITORY_TYPE.

    Returns:
        ChatMessageRepository: Repository instance

    Raises:
        ValueError: If repository_type is not supported
    """
    if repository_type is None:
        repository_type = ChatMessageRepositoryType(config.CHAT_MESSAGE_REPOSITORY_TYPE)

    if repository_type == ChatMessageRepositoryType.SQL:
        return SqlChatMessageRepository(db)
    else:
        raise ValueError(f"Unsupported chat message repository type: {repository_type}")
