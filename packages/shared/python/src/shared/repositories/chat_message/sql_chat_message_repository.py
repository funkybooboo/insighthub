"""SQL implementation of chat message repository."""

from sqlalchemy.orm import Session

from shared.models.chat import ChatMessage
from shared.types.option import Nothing, Option, Some

from .chat_message_repository import ChatMessageRepository


class SqlChatMessageRepository(ChatMessageRepository):
    """Repository for ChatMessage operations using SQL database."""

    def __init__(self, db: Session) -> None:
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self._db = db

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: str | None = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            extra_metadata=extra_metadata,
        )
        self._db.add(message)
        self._db.commit()
        self._db.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> Option[ChatMessage]:
        """Get chat message by ID."""
        message = (
            self._db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        )
        if message is None:
            return Nothing()
        return Some(message)

    def get_by_session(
        self, session_id: int, skip: int, limit: int
    ) -> list[ChatMessage]:
        """Get all messages for a chat session with pagination."""
        return (
            self._db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, message_id: int) -> bool:
        """Delete chat message by ID."""
        result = self.get_by_id(message_id)
        if result.is_nothing():
            return False

        message = result.unwrap()
        self._db.delete(message)
        self._db.commit()
        return True
