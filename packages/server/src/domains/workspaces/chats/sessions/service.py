"""Chat session service."""

from src.infrastructure.models import ChatSession
from src.infrastructure.repositories.chat_sessions import ChatSessionRepository


class ChatSessionService:
    """Service for managing chats sessions."""

    def __init__(self, repository: ChatSessionRepository):
        """Initialize service with repository."""
        self.repository = repository

    def create_session(
        self,
        user_id: int,
        title: str | None = None,
        workspace_id: int | None = None,
        rag_type: str = "vector",
    ) -> ChatSession:
        """Create a new chats session."""
        # Validate inputs
        if title and len(title.strip()) > 255:
            raise ValueError("Session title too long (max 255 characters)")

        if rag_type not in ["vector", "graph"]:
            raise ValueError("Invalid rag_type. Must be 'vector' or 'graph'")

        return self.repository.create(user_id, title.strip() if title else None, workspace_id, rag_type)

    def get_session(self, session_id: int) -> ChatSession | None:
        """Get session by ID."""
        return self.repository.get_by_id(session_id)

    def list_user_sessions(self, user_id: int, skip: int = 0, limit: int = 50) -> list[ChatSession]:
        """List sessions for a users."""
        return self.repository.get_by_user(user_id, skip, limit)



    def update_session(self, session_id: int, title: str | None = None) -> ChatSession | None:
        """Update session title."""
        # Validate inputs
        if title and len(title.strip()) > 255:
            raise ValueError("Session title too long (max 255 characters)")

        return self.repository.update(session_id, title=title.strip() if title else None)

    def delete_session(self, session_id: int) -> bool:
        """Delete a session."""
        return self.repository.delete(session_id)

    def validate_session_access(self, session_id: int, user_id: int) -> bool:
        """Validate that users has access to session."""
        session = self.repository.get_by_id(session_id)
        return session is not None and session.user_id == user_id

    def get_user_session(self, session_id: int, user_id: int) -> ChatSession | None:
        """Get session by ID for specific users."""
        session = self.repository.get_by_id(session_id)
        if session and session.user_id == user_id:
            return session
        return None

    def list_workspace_sessions(self, workspace_id: int, user_id: int) -> list[ChatSession]:
        """List sessions for a workspace (filtered by users access)."""
        # For now, return all sessions in workspace
        # TODO: Add proper workspace filtering
        return self.repository.get_by_workspace(workspace_id)