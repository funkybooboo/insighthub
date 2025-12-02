"""Session-specific DTOs for chat session."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateSessionRequest:
    """Request data for creating a chat session."""

    title: Optional[str] = None
    workspace_id: Optional[int] = None
    rag_type: str = "vector"


@dataclass
class UpdateSessionRequest:
    """Request data for updating a chat session."""

    title: Optional[str] = None


@dataclass
class SessionResponse:
    """Response data for a single chat session (single-user system)."""

    id: int
    workspace_id: Optional[int]
    title: Optional[str]
    rag_type: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "title": self.title,
            "rag_type": self.rag_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SessionListResponse:
    """Response data for listing chat session."""

    sessions: list[SessionResponse]
    count: int
    total: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session": [session.to_dict() for session in self.sessions],
            "count": self.count,
            "total": self.total,
        }
