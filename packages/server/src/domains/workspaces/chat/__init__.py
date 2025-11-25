"""Chat domain - handles chat sessions and messages."""

from shared.models import ChatMessage, ChatSession
from shared.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    SqlChatMessageRepository,
    SqlChatSessionRepository,
)

from .events import register_socket_handlers
from .routes import chat_bp
from .service import ChatService

__all__ = [
    "ChatSession",
    "ChatMessage",
    "ChatSessionRepository",
    "SqlChatSessionRepository",
    "ChatMessageRepository",
    "SqlChatMessageRepository",
    "ChatService",
    "chat_bp",
    "register_socket_handlers",
]
