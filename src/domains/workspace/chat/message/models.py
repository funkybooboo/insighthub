"""Chat message model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatMessage:
    """Chat message model for storing conversation history."""

    id: int
    session_id: int
    role: str  # 'users', 'assistant', 'system'
    content: str
    extra_metadata: str | None = None  # JSON string for storing additional data
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role={self.role}, content='{content_preview}')>"
