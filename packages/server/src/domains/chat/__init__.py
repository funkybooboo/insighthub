"""Chat domain - handles chat sessions and messages."""

from shared.models import ChatMessage, ChatSession
from shared.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    SqlChatMessageRepository,
    SqlChatSessionRepository,
)

from .routes import chat_bp
from .service import ChatService
from .socket_handlers import register_socket_handlers

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
