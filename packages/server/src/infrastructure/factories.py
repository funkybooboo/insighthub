"""Factory functions for creating repository instances using SqlDatabase."""

from shared.database.sql import SqlDatabase
from shared.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    SqlChatMessageRepository,
    SqlChatSessionRepository,
    SqlDocumentRepository,
    SqlUserRepository,
    UserRepository,
)


def create_user_repository(db: SqlDatabase) -> UserRepository:
    """Create a user repository instance."""
    return SqlUserRepository(db)


def create_document_repository(db: SqlDatabase) -> DocumentRepository:
    """Create a document repository instance."""
    return SqlDocumentRepository(db)


def create_chat_session_repository(db: SqlDatabase) -> ChatSessionRepository:
    """Create a chat session repository instance."""
    return SqlChatSessionRepository(db)


def create_chat_message_repository(db: SqlDatabase) -> ChatMessageRepository:
    """Create a chat message repository instance."""
    return SqlChatMessageRepository(db)
