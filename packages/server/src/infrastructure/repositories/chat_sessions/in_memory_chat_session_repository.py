"""In-memory implementation of ChatSessionRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.models import ChatSession

from .chat_session_repository import ChatSessionRepository


class InMemoryChatSessionRepository(ChatSessionRepository):
    """In-memory implementation of ChatSessionRepository for development/testing."""

    def __init__(self):
        """Initialize the repository."""
        self._sessions: dict[int, ChatSession] = {}
        self._next_id = 1

    def create(
        self,
        user_id: int,
        title: str | None = None,
        workspace_id: int | None = None,
        rag_type: str = "vector",
    ) -> ChatSession:
        """Create a new chats session."""
        session = ChatSession(
            id=self._next_id,
            user_id=user_id,
            workspace_id=workspace_id,
            title=title,
            rag_type=rag_type,
        )
        self._sessions[self._next_id] = session
        self._next_id += 1
        return session

    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[ChatSession]:
        """Get sessions by users ID with pagination."""
        user_sessions = [s for s in self._sessions.values() if s.user_id == user_id]
        return user_sessions[skip : skip + limit]

    def get_by_workspace(
        self, workspace_id: int, skip: int = 0, limit: int = 50
    ) -> list[ChatSession]:
        """Get sessions by workspace ID with pagination."""
        workspace_sessions = [s for s in self._sessions.values() if s.workspace_id == workspace_id]
        return workspace_sessions[skip : skip + limit]

    def update(self, session_id: int, **kwargs) -> Optional[ChatSession]:
        """Update session fields."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.updated_at = datetime.utcnow()
        return session

    def delete(self, session_id: int) -> bool:
        """Delete session by ID."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
