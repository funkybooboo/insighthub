"""Chat service combining message and session management."""

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
