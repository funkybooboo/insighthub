"""SQL implementation of ChatMessageRepository."""

from datetime import datetime
from typing import Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.message.models import ChatMessage
from src.infrastructure.logger import create_logger
from src.infrastructure.sql_database import DatabaseException, SqlDatabase
from src.infrastructure.types import DatabaseError, PaginatedResult, Pagination

logger = create_logger(__name__)


class ChatMessageRepository:
    """SQL implementation of chat message repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: Optional[str] = None,
    ) -> Result[ChatMessage, DatabaseError]:
        """Create a new chat message."""
        query = """
            INSERT INTO chat_messages (chat_session_id, role, content, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        try:
            result = self.db.fetch_one(
                query,
                (
                    session_id,
                    role,
                    content,
                    datetime.utcnow(),
                ),
            )
        except DatabaseException as e:
            logger.error(f"Database error creating chat message: {e}")
            return Failure(DatabaseError(e.message, operation="create_chat_message"))

        if not result:
            return Failure(
                DatabaseError("Insert returned no result", operation="create_chat_message")
            )

        return Success(
            ChatMessage(
                id=result["id"],
                session_id=session_id,
                role=role,
                content=content,
                extra_metadata=extra_metadata,
            )
        )

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get message by ID."""
        query = """
            SELECT id, chat_session_id as session_id, role, content, created_at
            FROM chat_messages WHERE id = %s
        """
        try:
            result = self.db.fetch_one(query, (message_id,))
        except DatabaseException as e:
            logger.error(f"Database error getting chat message: {e}")
            return None

        if result:
            return ChatMessage(**result)
        return None

    def get_by_session(
        self, session_id: int, pagination: Pagination
    ) -> PaginatedResult[ChatMessage]:
        """Get message for a session with pagination."""
        skip, limit = pagination.offset_limit()

        # Get total count for session
        count_query = "SELECT COUNT(*) as total FROM chat_messages WHERE chat_session_id = %s"
        try:
            count_result = self.db.fetch_one(count_query, (session_id,))
            total_count = count_result["total"] if count_result else 0
        except DatabaseException as e:
            logger.error(f"Database error counting chat messages: {e}")
            total_count = 0

        # Get paginated results
        query = """
            SELECT id, chat_session_id as session_id, role, content, created_at
            FROM chat_messages WHERE chat_session_id = %s
            ORDER BY created_at ASC
            LIMIT %s OFFSET %s
        """
        try:
            results = self.db.fetch_all(query, (session_id, limit, skip))
            items = [ChatMessage(**result) for result in results]
        except DatabaseException as e:
            logger.error(f"Database error getting chat messages: {e}")
            items = []

        return PaginatedResult(items=items, total_count=total_count, skip=skip, limit=limit)

    def delete(self, message_id: int) -> bool:
        """Delete message by ID."""
        query = "DELETE FROM chat_messages WHERE id = %s"
        try:
            affected_rows = self.db.execute(query, (message_id,))
        except DatabaseException as e:
            logger.error(f"Database error deleting chat message: {e}")
            return False

        return affected_rows > 0
