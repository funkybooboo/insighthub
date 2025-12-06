"""Chat session model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from src.domains.workspace.chat.message.models import ChatMessage


@dataclass
class ChatSession:
    """Represents a chat session in a workspace."""

    id: int
    workspace_id: int
    title: Optional[str] = None
    rag_type: str = "vector"
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, title={self.title})>"
