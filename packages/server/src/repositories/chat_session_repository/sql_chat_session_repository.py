"""SQL implementation of ChatSessionRepository."""

from typing import Optional

from sqlalchemy.orm import Session

from src.models import ChatSession

from .chat_session_repository import ChatSessionRepository


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
        self, user_id: int, title: Optional[str] = None, rag_type: str = "vector"
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(user_id=user_id, title=title, rag_type=rag_type)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
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

    def update(self, session_id: int, **kwargs: str) -> Optional[ChatSession]:
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
