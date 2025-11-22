"""Status update event schemas for real-time UI updates."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DocumentStatusEvent:
    """
    Published when a document's processing status changes.

    Used to update UI in real-time via Socket.IO.
    Routing key: document.status.updated
    """

    document_id: int
    workspace_id: int
    status: str  # 'pending', 'processing', 'ready', 'failed'
    message: str | None = None
    error: str | None = None
    progress: int | None = None  # 0-100 for progress bar
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class WorkspaceStatusEvent:
    """
    Published when a workspace's status changes.

    Used to update UI in real-time via Socket.IO.
    Routing key: workspace.status.updated
    """

    workspace_id: int
    user_id: int
    status: str  # 'provisioning', 'ready', 'error'
    message: str | None = None
    error: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
