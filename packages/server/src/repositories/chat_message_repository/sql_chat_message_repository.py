"""SQL implementation of ChatMessageRepository."""

from typing import Optional

from sqlalchemy.orm import Session

from src.models import ChatMessage

from .chat_message_repository import ChatMessageRepository


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
        extra_metadata: Optional[str] = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            session_id=session_id, role=role, content=content, extra_metadata=extra_metadata
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        return self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    def get_by_session(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
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
