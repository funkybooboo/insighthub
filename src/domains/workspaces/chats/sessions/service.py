"""Chat session service."""

from src.infrastructure.logger import create_logger
from src.infrastructure.models import ChatSession
from src.infrastructure.repositories.chat_sessions import ChatSessionRepository

logger = create_logger(__name__)


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
        logger.info(
            f"Creating chat session: user_id={user_id}, workspace_id={workspace_id}, rag_type='{rag_type}'"
        )

        # Validate inputs
        if title and len(title.strip()) > 255:
            logger.error(f"Session creation failed: title too long (user_id={user_id})")
            raise ValueError("Session title too long (max 255 characters)")

        if rag_type not in ["vector", "graph"]:
            logger.error(
                f"Session creation failed: invalid rag_type '{rag_type}' (user_id={user_id})"
            )
            raise ValueError("Invalid rag_type. Must be 'vector' or 'graph'")

        session = self.repository.create(
            user_id, title.strip() if title else None, workspace_id, rag_type
        )

        logger.info(f"Chat session created: session_id={session.id}, user_id={user_id}")

        return session

    def get_session(self, session_id: int) -> ChatSession | None:
        """Get session by ID."""
        return self.repository.get_by_id(session_id)

    def list_user_sessions(self, user_id: int, skip: int = 0, limit: int = 50) -> list[ChatSession]:
        """List sessions for a users."""
        return self.repository.get_by_user(user_id, skip, limit)

    def update_session(self, session_id: int, title: str | None = None) -> ChatSession | None:
        """Update session title."""
        logger.info(f"Updating chat session: session_id={session_id}, new_title='{title}'")

        # Validate inputs
        if title and len(title.strip()) > 255:
            logger.error(f"Session update failed: title too long (session_id={session_id})")
            raise ValueError("Session title too long (max 255 characters)")

        updated_session = self.repository.update(session_id, title=title.strip() if title else None)

        if updated_session:
            logger.info(f"Chat session updated: session_id={session_id}")
        else:
            logger.warning(
                f"Chat session update failed: session not found (session_id={session_id})"
            )

        return updated_session

    def delete_session(self, session_id: int) -> bool:
        """Delete a session."""
        logger.info(f"Deleting chat session: session_id={session_id}")

        deleted = self.repository.delete(session_id)

        if deleted:
            logger.info(f"Chat session deleted: session_id={session_id}")
        else:
            logger.warning(
                f"Chat session deletion failed: session not found (session_id={session_id})"
            )

        return deleted

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

    def get_workspace_session(
        self, workspace_id: int, session_id: int, user_id: int
    ) -> ChatSession | None:
        """Get session by ID with workspace and user validation."""
        session = self.repository.get_by_id(session_id)
        if session and session.user_id == user_id and session.workspace_id == workspace_id:
            return session
        return None

    def list_workspace_sessions(
        self, workspace_id: int, user_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[ChatSession], int]:
        """List sessions for a workspace (filtered by users access)."""
        # Get all sessions in workspace and filter by user
        all_sessions = self.repository.get_by_workspace(workspace_id)
        user_sessions = [s for s in all_sessions if s.user_id == user_id]

        # Apply pagination
        paginated_sessions = user_sessions[skip : skip + limit]
        total = len(user_sessions)

        return paginated_sessions, total
