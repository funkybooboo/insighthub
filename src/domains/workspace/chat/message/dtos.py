"""Message-specific DTOs for chat message."""

from dataclasses import dataclass
from typing import Callable, Optional

# ============================================================================
# Request DTOs (User Input)
# ============================================================================


@dataclass
class SendMessageRequest:
    """Request DTO for sending a message with RAG."""

    session_id: int
    content: str
    stream_callback: Optional[Callable[[str], None]] = None


@dataclass
class ListMessagesRequest:
    """Request DTO for listing messages."""

    session_id: int
    skip: int = 0
    limit: int = 50


# ============================================================================
# Response DTOs (Service Output)
# ============================================================================


@dataclass
class MessageResponse:
    """Response DTO for a single chat message."""

    id: int
    session_id: int
    role: str
    content: str
    extra_metadata: Optional[str]
    created_at: str
    updated_at: str
