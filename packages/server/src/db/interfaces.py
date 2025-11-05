"""Repository interfaces for database operations."""

from abc import ABC, abstractmethod
from typing import Optional

from .models import ChatMessage, ChatSession, Document, User


class UserRepository(ABC):
    """Interface for User repository operations."""

    @abstractmethod
    def create(self, username: str, email: str, full_name: Optional[str] = None) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        pass

    @abstractmethod
    def update(self, user_id: int, **kwargs: str) -> Optional[User]:
        """Update user fields."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        pass


class DocumentRepository(ABC):
    """Interface for Document repository operations."""

    @abstractmethod
    def create(
        self,
        user_id: int,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        content_hash: str,
        chunk_count: Optional[int] = None,
        rag_collection: Optional[str] = None,
    ) -> Document:
        """Create a new document."""
        pass

    @abstractmethod
    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get documents by user ID with pagination."""
        pass

    @abstractmethod
    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        pass

    @abstractmethod
    def update(self, document_id: int, **kwargs: str | int) -> Optional[Document]:
        """Update document fields."""
        pass

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        pass


class ChatSessionRepository(ABC):
    """Interface for ChatSession repository operations."""

    @abstractmethod
    def create(
        self, user_id: int, title: Optional[str] = None, rag_type: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID."""
        pass

    @abstractmethod
    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatSession]:
        """Get sessions by user ID with pagination."""
        pass

    @abstractmethod
    def update(self, session_id: int, **kwargs: str) -> Optional[ChatSession]:
        """Update session fields."""
        pass

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """Delete session by ID."""
        pass


class ChatMessageRepository(ABC):
    """Interface for ChatMessage repository operations."""

    @abstractmethod
    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: Optional[str] = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get message by ID."""
        pass

    @abstractmethod
    def get_by_session(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
        """Get messages by session ID with pagination."""
        pass

    @abstractmethod
    def delete(self, message_id: int) -> bool:
        """Delete message by ID."""
        pass
