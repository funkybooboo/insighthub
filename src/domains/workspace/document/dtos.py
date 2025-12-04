"""Data Transfer Objects for document operations."""

from dataclasses import dataclass
from typing import Optional

# ============================================================================
# Request DTOs (User Input)
# ============================================================================


@dataclass
class UploadDocumentRequest:
    """Request DTO for uploading a document."""

    workspace_id: int
    filename: str
    file_path: str  # Path to file on disk


@dataclass
class ShowDocumentRequest:
    """Request DTO for showing document details."""

    document_id: int
    workspace_id: int


@dataclass
class DeleteDocumentRequest:
    """Request DTO for deleting a document."""

    document_id: int
    workspace_id: int


# ============================================================================
# Response DTOs (Service Output)
# ============================================================================


@dataclass
class DocumentResponse:
    """Response DTO for a single document."""

    id: int
    workspace_id: int
    filename: str
    file_size: int
    mime_type: str
    chunk_count: Optional[int]
    status: str
    content_hash: Optional[str]
    created_at: str
