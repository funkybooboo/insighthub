"""Workspace domain models for InsightHub."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from shared.types.common import DocumentStatus


@dataclass
class Workspace:
    """
    Represents a workspace in InsightHub.

    A workspace is a container for documents, chat sessions, and RAG configuration.
    It allows users to group related documents and maintain separate chat contexts.
    """

    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    user_id: str  # Owner of the workspace

    # Optional workspace settings
    description: Optional[str] = None
    is_active: bool = True


@dataclass
class RagConfig:
    """
    RAG configuration for a workspace.

    Each workspace has exactly one RAG configuration that determines
    how documents are processed and queries are answered.
    """

    id: str
    workspace_id: str
    embedding_model: str
    retriever_type: str
    chunk_size: int
    created_at: datetime
    updated_at: datetime

    # Fields with defaults must come after required fields
    chunk_overlap: int = 0
    top_k: int = 8
    embedding_dim: Optional[int] = None
    rerank_enabled: bool = False
    rerank_model: Optional[str] = None


@dataclass
class WorkspaceDocument:
    """
    Document within a workspace.

    Extends the base Document type with workspace-specific information.
    """

    id: str
    workspace_id: str
    filename: str
    storage_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    user_id: str  # Who uploaded it

    # Document processing status
    status: DocumentStatus = DocumentStatus.PENDING
    processing_error: Optional[str] = None
    chunk_count: Optional[int] = None
    embedding_status: Optional[str] = None

    # Optional extracted metadata
    title: Optional[str] = None
    author: Optional[str] = None
    created_date: Optional[datetime] = None


@dataclass
class ChatSession:
    """
    Chat session within a workspace.

    Each chat session maintains its own conversation history
    but has access to all documents in the workspace.
    """

    id: str
    workspace_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    user_id: str  # Who created the session

    # Optional session settings
    is_active: bool = True
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class ChatMessage:
    """
    Individual message within a chat session.
    """

    id: str
    session_id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    created_at: datetime
    token_count: Optional[int] = None
    model_used: Optional[str] = None
    retrieval_results: Optional[list[dict]] = None  # For assistant messages


@dataclass
class WorkspaceStats:
    """
    Statistics for a workspace.
    """

    workspace_id: str
    document_count: int
    total_document_size: int
    chunk_count: int
    chat_session_count: int
    total_message_count: int
    last_activity: Optional[datetime] = None
