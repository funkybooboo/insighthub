"""Chat session service."""

from typing import Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.session.data_access import ChatSessionDataAccess
from src.domains.workspace.chat.session.models import ChatSession
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.options import get_valid_rag_types, is_valid_rag_type
from src.infrastructure.types import (
    DatabaseError,
    NotFoundError,
    PaginatedResult,
    Pagination,
    ValidationError,
)

logger = create_logger(__name__)


class ChatSessionService:
    """Service for managing chat session."""

    def __init__(self, data_access: ChatSessionDataAccess):
        """Initialize service with data access layer."""
        self.data_access = data_access

    def create_session(
        self,
        title: Optional[str] = None,
        workspace_id: Optional[int] = None,
        rag_type: str = "vector",
    ) -> Result[ChatSession, ValidationError | DatabaseError]:
        """Create a new chat session (single-user system)."""
        logger.info(f"Creating chat session: workspace_id={workspace_id}, rag_type='{rag_type}'")

        # Validate inputs
        if not title or not title.strip():  # Added check for empty/whitespace title
            logger.error("Session creation failed: title cannot be empty")
            return Failure(ValidationError("Session title cannot be empty", field="title"))
        if len(title.strip()) > 255:
            logger.error("Session creation failed: title too long")
            return Failure(
                ValidationError("Session title too long (max 255 characters)", field="title")
            )

        if not is_valid_rag_type(rag_type):
            valid_types = get_valid_rag_types()
            logger.error(f"Session creation failed: invalid rag_type '{rag_type}'")
            return Failure(
                ValidationError(
                    f"Invalid rag_type. Must be one of: {', '.join(valid_types)}", field="rag_type"
                )
            )

        create_result = self.data_access.create(
            title.strip() if title else None, workspace_id, rag_type
        )
        if isinstance(create_result, Failure):
            return Failure(create_result.failure())

        session = create_result.unwrap()
        logger.info(f"Chat session created: session_id={session.id}")

        return Success(session)

    def get_session(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID."""
        return self.data_access.get_by_id(session_id)

    def list_sessions(self, pagination: Pagination) -> PaginatedResult[ChatSession]:
        """List all chat session (single-user system)."""
        return self.data_access.get_all(pagination)

    def update_session(
        self, session_id: int, title: Optional[str] = None
    ) -> Result[ChatSession, ValidationError | NotFoundError]:
        """Update session title."""
        logger.info(f"Updating chat session: session_id={session_id}, new_title='{title}'")

        # Validate inputs
        if title and len(title.strip()) > 255:
            logger.error(f"Session update failed: title too long (session_id={session_id})")
            return Failure(
                ValidationError("Session title too long (max 255 characters)", field="title")
            )

        updated_session = self.data_access.update(
            session_id, title=title.strip() if title else None
        )

        if updated_session:
            logger.info(f"Chat session updated: session_id={session_id}")
            return Success(updated_session)
        else:
            logger.warning(
                f"Chat session update failed: session not found (session_id={session_id})"
            )
            return Failure(NotFoundError("chat_session", session_id))

    def delete_session(self, session_id: int) -> bool:
        """Delete a session."""
        logger.info(f"Deleting chat session: session_id={session_id}")

        deleted = self.data_access.delete(session_id)

        if deleted:
            logger.info(f"Chat session deleted: session_id={session_id}")
        else:
            logger.warning(
                f"Chat session deletion failed: session not found (session_id={session_id})"
            )

        return deleted

    def get_workspace_session(self, workspace_id: int, session_id: int) -> Optional[ChatSession]:
        """Get session by ID with workspace validation (single-user system)."""
        session = self.data_access.get_by_id(session_id)
        if session and session.workspace_id == workspace_id:
            return session
        return None

    def list_workspace_sessions(
        self, workspace_id: int, pagination: Pagination
    ) -> PaginatedResult[ChatSession]:
        """List session for a workspace (single-user system)."""
        return self.data_access.get_by_workspace(workspace_id, pagination)
