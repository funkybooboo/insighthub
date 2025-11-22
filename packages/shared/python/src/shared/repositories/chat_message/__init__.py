"""Chat message repository module."""

from shared.repositories.chat_message.chat_message_repository import (
    ChatMessageRepository,
)
from shared.repositories.chat_message.sql_chat_message_repository import (
    SqlChatMessageRepository,
)

__all__ = [
    "ChatMessageRepository",
    "SqlChatMessageRepository",
]
