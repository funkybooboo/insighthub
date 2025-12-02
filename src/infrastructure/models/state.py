"""State model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class State:
    """Application state for tracking current workspace and session selections."""

    id: int
    current_workspace_id: Optional[int] = None
    current_session_id: Optional[int] = None
    updated_at: datetime = datetime.utcnow()
