"""Database package for SQLAlchemy models and database operations."""

from . import models
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

__all__ = [
    "models",
    # Interfaces
    "UserRepository",
    "DocumentRepository",
    "ChatSessionRepository",
    "ChatMessageRepository",
    # Implementations
    "SqlUserRepository",
    "SqlDocumentRepository",
    "SqlChatSessionRepository",
    "SqlChatMessageRepository",
]
