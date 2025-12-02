"""Chat session model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatSession:
    """Chat session model for grouping related chat message."""

    id: int
    workspace_id: int | None = None
    title: str | None = None
    rag_type: str = "vector"  # 'vector' or 'graph'
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, title={self.title})>"
