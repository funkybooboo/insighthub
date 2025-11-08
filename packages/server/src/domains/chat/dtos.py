"""Data Transfer Objects for chat operations."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatRequest:
    """Request data for chat endpoint."""

    message: str
    session_id: int | None = None
    rag_type: str = "vector"


@dataclass
class ContextChunk:
    """Context chunk from RAG system."""

    text: str
    score: float
    metadata: dict[str, str]

    def to_dict(self) -> dict[str, str | float | dict[str, str]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "score": self.score,
            "metadata": self.metadata,
        }


@dataclass
class ChatResponse:
    """Response data for chat endpoint."""

    answer: str
    context: list[ContextChunk]
    session_id: int
    documents_count: int

    def to_dict(self) -> dict[str, str | list[dict[str, str | float | dict[str, str]]] | int]:
        """Convert to dictionary for JSON serialization."""
        return {
            "answer": self.answer,
            "context": [chunk.to_dict() for chunk in self.context],
            "session_id": self.session_id,
            "documents_count": self.documents_count,
        }


@dataclass
class SessionResponse:
    """Response data for a chat session."""

    id: int
    title: str
    rag_type: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, str | int]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "rag_type": self.rag_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SessionListResponse:
    """Response data for listing sessions."""

    sessions: list[SessionResponse]
    count: int

    def to_dict(self) -> dict[str, list[dict[str, str | int]] | int]:
        """Convert to dictionary for JSON serialization."""
        return {
            "sessions": [session.to_dict() for session in self.sessions],
            "count": self.count,
        }


@dataclass
class MessageResponse:
    """Response data for a chat message."""

    id: int
    role: str
    content: str
    metadata: dict[str, str | int] | None
    created_at: datetime

    def to_dict(self) -> dict[str, str | int | dict[str, str | int] | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SessionMessagesResponse:
    """Response data for session messages."""

    messages: list[MessageResponse]
    count: int

    def to_dict(self) -> dict[str, list[dict[str, str | int | dict[str, str | int] | None]] | int]:
        """Convert to dictionary for JSON serialization."""
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "count": self.count,
        }
