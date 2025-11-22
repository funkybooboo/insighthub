"""SQL implementation of chat session repository."""

from sqlalchemy.orm import Session

from shared.models.chat import ChatSession
from shared.types.option import Nothing, Option, Some

from .chat_session_repository import ChatSessionRepository


class SqlChatSessionRepository(ChatSessionRepository):
    """Repository for ChatSession operations using SQL database."""

    def __init__(self, db: Session) -> None:
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self._db = db

    def create(
        self, user_id: int, title: str | None = None, rag_type: str | None = "vector"
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(user_id=user_id, title=title, rag_type=rag_type)
        self._db.add(session)
        self._db.commit()
        self._db.refresh(session)
        return session

    def get_by_id(self, session_id: int) -> Option[ChatSession]:
        """Get chat session by ID."""
        session = (
            self._db.query(ChatSession).filter(ChatSession.id == session_id).first()
        )
        if session is None:
            return Nothing()
        return Some(session)

    def get_by_user(self, user_id: int, skip: int, limit: int) -> list[ChatSession]:
        """Get all chat sessions for a user with pagination."""
        return (
            self._db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, session_id: int, **kwargs: str) -> Option[ChatSession]:
        """Update chat session fields."""
        result = self.get_by_id(session_id)
        if result.is_nothing():
            return Nothing()

        session = result.unwrap()
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        self._db.commit()
        self._db.refresh(session)
        return Some(session)

    def delete(self, session_id: int) -> bool:
        """Delete chat session by ID."""
        result = self.get_by_id(session_id)
        if result.is_nothing():
            return False

        session = result.unwrap()
        self._db.delete(session)
        self._db.commit()
        return True
