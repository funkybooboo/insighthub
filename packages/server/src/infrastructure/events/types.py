"""Unified event type definitions for the application."""

import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


# Base Event Structure
class EventData(BaseModel):
    """Base structure for event data payloads."""

    event_type: str = Field(..., description="Event type identifier")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    user_id: Optional[int] = Field(None, description="User ID associated with event")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")


# Document Events
class DocumentStatusData(BaseModel):
    """Document processing status update event data."""

    event_type: str = "document.status.updated"
    document_id: int
    workspace_id: Optional[int] = None
    filename: str
    status: str  # 'pending', 'parsing', 'chunking', 'embedding', 'indexing', 'ready', 'failed'
    progress: Optional[int] = None
    chunk_count: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class DocumentProcessingData(BaseModel):
    """Document processing pipeline event data."""

    event_type: str = "document.processing.step"
    document_id: int
    workspace_id: Optional[int] = None
    step: str  # 'parsed', 'chunked', 'embedded', 'indexed'
    filename: str
    details: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class DocumentParsedData(BaseModel):
    """Document parsed event data."""

    event_type: str = "document.parsed"
    document_id: int
    workspace_id: Optional[int] = None
    filename: str
    text_length: int
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class DocumentChunkedData(BaseModel):
    """Document chunked event data."""

    event_type: str = "document.chunked"
    document_id: int
    workspace_id: Optional[int] = None
    filename: str
    chunk_count: int
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class DocumentEmbeddedData(BaseModel):
    """Document embedded event data."""

    event_type: str = "document.embedded"
    document_id: int
    workspace_id: Optional[int] = None
    filename: str
    embedding_count: int
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class DocumentIndexedData(BaseModel):
    """Document indexed event data."""

    event_type: str = "document.indexed"
    document_id: int
    workspace_id: Optional[int] = None
    filename: str
    chunk_count: int
    collection_name: str
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


# Workspace Events
class WorkspaceStatusData(BaseModel):
    """Workspace operation status update event data."""

    event_type: str = "workspace.status.updated"
    workspace_id: int
    status: str  # 'provisioning', 'ready', 'failed', 'deleting', 'deleted'
    operation: Optional[str] = None  # 'create', 'delete', 'update'
    error: Optional[str] = None
    message: Optional[str] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class WorkspaceOperationCompleteData(BaseModel):
    """Workspace operation completion event data."""

    event_type: str = "workspace.operation.complete"
    workspace_id: int
    operation: str  # 'create', 'delete', 'update'
    status: str  # 'ready', 'failed'
    error: Optional[str] = None
    message: Optional[str] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


# Chat Events
class ChatMessageData(BaseModel):
    """Chat message related event data."""

    event_type: str = "chat.message.created"
    session_id: int
    workspace_id: int
    message_id: int
    role: str  # 'user', 'assistant', 'system'
    content: str
    token_count: Optional[int] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class ChatResponseData(BaseModel):
    """Chat response streaming event data."""

    event_type: str = "chat.response.stream"
    session_id: int
    workspace_id: int
    chunk: str
    is_complete: bool = False
    total_tokens: Optional[int] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class ChatResponseCompleteData(BaseModel):
    """Chat response completion event data."""

    event_type: str = "chat.response.complete"
    session_id: int
    workspace_id: int
    message_id: int
    full_response: str
    total_tokens: int
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class ChatErrorData(BaseModel):
    """Chat error event data."""

    event_type: str = "chat.error"
    session_id: int
    workspace_id: int
    message_id: int
    error: str
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


# System Events
class SystemHealthData(BaseModel):
    """System health status event data."""

    event_type: str = "system.health.updated"
    component: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    metrics: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class WorkerTaskData(BaseModel):
    """Background worker task event data."""

    event_type: str = "worker.task.status"
    worker_type: str  # 'document_processor', 'chat_query', 'workspace_manager'
    task_id: str
    status: str  # 'started', 'running', 'completed', 'failed'
    progress: Optional[int] = None
    error: Optional[str] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


# Legacy Event Types (for backward compatibility during transition)
class LegacyDocumentStatusData(BaseModel):
    """Legacy document status data structure."""

    document_id: int
    user_id: int
    workspace_id: Optional[int] = None
    status: str
    error: Optional[str] = None
    message: Optional[str] = None
    progress: Optional[int] = None
    chunk_count: Optional[int] = None
    filename: str
    timestamp: str


class LegacyWorkspaceStatusData(BaseModel):
    """Legacy workspace status data structure."""

    workspace_id: int
    user_id: int
    status: str
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str
