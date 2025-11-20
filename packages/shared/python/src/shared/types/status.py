"""Status type definitions shared across the application."""

from enum import Enum


class DocumentProcessingStatus(str, Enum):
    """Document processing status enum."""

    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class WorkspaceStatus(str, Enum):
    """Workspace provisioning status enum."""

    PROVISIONING = "provisioning"
    READY = "ready"
    ERROR = "error"
