"""Chat models."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatSession:
    """Chat session model for grouping related chat messages."""

    id: int
    user_id: int
    workspace_id: int | None = None
    title: str | None = None
    rag_type: str = "vector"  # 'vector' or 'graph'
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title={self.title})>"


@dataclass
class ChatMessage:
    """Chat message model for storing conversation history."""

    id: int
    session_id: int
    role: str  # 'user', 'assistant', 'system'
    content: str
    extra_metadata: str | None = None  # JSON string for storing additional data
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role={self.role}, content='{content_preview}')>"
