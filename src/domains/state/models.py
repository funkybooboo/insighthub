"""State model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional


@dataclass
class State:
    """Represents the CLI state."""

    id: int = 1
    current_workspace_id: Optional[int] = None
    current_session_id: Optional[int] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<State(workspace={self.current_workspace_id}, session={self.current_session_id})>"
