"""Chat repositories."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from shared.models.chat import ChatMessage, ChatSession


class ChatSessionRepository(ABC):
    """Interface for ChatSession repository operations."""

    @abstractmethod
    def create(
        self, user_id: int, title: str | None = None, rag_type: str | None = None
    ) -> ChatSession:
        """Create a new chat session."""
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> ChatSession | None:
        """Get session by ID."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ChatSession]:
        """Get sessions by user ID with pagination."""
        pass

    @abstractmethod
    def update(self, session_id: int, **kwargs: str) -> ChatSession | None:
        """Update session fields."""
        pass

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """Delete session by ID."""
        pass


class SqlChatSessionRepository(ChatSessionRepository):
    """Repository for ChatSession operations using SQL database."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(
        self, user_id: int, title: str | None = None, rag_type: str | None = "vector"
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(user_id=user_id, title=title, rag_type=rag_type)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: int) -> ChatSession | None:
        """Get chat session by ID."""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[ChatSession]:
        """Get all chat sessions for a user with pagination."""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, session_id: int, **kwargs: str) -> ChatSession | None:
        """Update chat session fields."""
        session = self.get_by_id(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            self.db.commit()
            self.db.refresh(session)
        return session

    def delete(self, session_id: int) -> bool:
        """Delete chat session by ID."""
        session = self.get_by_id(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False


class ChatMessageRepository(ABC):
    """Interface for ChatMessage repository operations."""

    @abstractmethod
    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: str | None = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> ChatMessage | None:
        """Get message by ID."""
        pass

    @abstractmethod
    def get_by_session(self, session_id: int, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
        """Get messages by session ID with pagination."""
        pass

    @abstractmethod
    def delete(self, message_id: int) -> bool:
        """Delete message by ID."""
        pass


class SqlChatMessageRepository(ChatMessageRepository):
    """Repository for ChatMessage operations using SQL database."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: str | None = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            session_id=session_id, role=role, content=content, extra_metadata=extra_metadata
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> ChatMessage | None:
        """Get chat message by ID."""
        return self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    def get_by_session(self, session_id: int, skip: int = 0, limit: int = 100) -> list[ChatMessage]:
        """Get all messages for a chat session with pagination."""
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, message_id: int) -> bool:
        """Delete chat message by ID."""
        message = self.get_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False
