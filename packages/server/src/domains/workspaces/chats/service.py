"""Chat service combining message and session management."""

from flask import g

from src.domains.workspaces.chats.messages.service import ChatMessageService
from src.domains.workspaces.chats.sessions.service import ChatSessionService
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class ChatService:
    """Unified service for chat operations combining messages and sessions."""

    def __init__(self, message_service: ChatMessageService, session_service: ChatSessionService):
        """Initialize with message and session services."""
        self.message_service = message_service
        self.session_service = session_service

    def retry_pending_rag_queries(self, workspace_id: int, user_id: int) -> None:
        """
        Retry any pending RAG queries for a workspace.

        This is called when a document is indexed and becomes available for queries.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID
        """
        try:
            # Get LLM provider from app context
            if not hasattr(g, "app_context") or not hasattr(g.app_context, "llm_provider"):
                logger.warning("LLM provider not available in app context")
                return

            llm_provider = g.app_context.llm_provider

            # For now, just log that we'd retry queries
            # In a full implementation, this would:
            # 1. Find pending queries for this workspace
            # 2. Re-execute them with the new document available
            # 3. Update query status and send results

            logger.info(f"Would retry pending RAG queries for workspace {workspace_id}, user {user_id}")
            logger.debug(f"Using LLM provider: {type(llm_provider).__name__}")

            # TODO: Implement actual retry logic when pending query storage is available

        except Exception as e:
            logger.error(f"Failed to retry pending RAG queries: {e}")