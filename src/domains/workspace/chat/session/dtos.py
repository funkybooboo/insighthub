"""Session-specific DTOs for chat session."""

from dataclasses import dataclass
from typing import Optional

# ============================================================================
# Request DTOs (User Input)
# ============================================================================


@dataclass
class CreateSessionRequest:
    """Request DTO for creating a chat session."""

    workspace_id: int
    title: Optional[str] = None
    rag_type: Optional[str] = None


@dataclass
class UpdateSessionRequest:
    """Request DTO for updating a chat session."""

    session_id: int
    title: Optional[str] = None


@dataclass
class DeleteSessionRequest:
    """Request DTO for deleting a chat session."""

    session_id: int


@dataclass
class SelectSessionRequest:
    """Request DTO for selecting a chat session."""

    session_id: int


@dataclass
class ListSessionsRequest:
    """Request DTO for listing sessions."""

    workspace_id: int
    skip: int = 0
    limit: int = 50


# ============================================================================
# Response DTOs (Service Output)
# ============================================================================


@dataclass
class SessionResponse:
    """Response DTO for a single chat session."""

    id: int
    workspace_id: Optional[int]
    title: Optional[str]
    rag_type: str
    created_at: str
    updated_at: str
