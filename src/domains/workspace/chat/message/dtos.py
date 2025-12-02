"""Message-specific DTOs for chat message."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CreateMessageRequest:
    """Request data for creating a chat message."""

    content: str
    role: str = "users"  # 'users', 'assistant', 'system'


@dataclass
class MessageResponse:
    """Response data for a single chat message."""

    id: int
    session_id: int
    role: str
    content: str
    extra_metadata: str | None
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class MessageListResponse:
    """Response data for listing chat message."""

    messages: list[MessageResponse]
    count: int
    total: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "message": [message.to_dict() for message in self.messages],
            "count": self.count,
            "total": self.total,
        }
