"""Data Transfer Objects for document operations."""

from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO

from src.infrastructure.models import Document


@dataclass
class DocumentUploadRequest:
    """Request data for uploading a document."""

    filename: str
    file_obj: BinaryIO
    mime_type: str


@dataclass
class DocumentResponse:
    """Response data for a single document."""

    id: int
    filename: str
    file_size: int
    mime_type: str
    chunk_count: int | None
    processing_status: str
    processing_error: str | None
    created_at: datetime

    def to_dict(self) -> dict[str, str | int | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "chunk_count": self.chunk_count,
            "processing_status": self.processing_status,
            "processing_error": self.processing_error,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class DocumentUploadResult:
    """Result data for document upload operation."""

    document: Document | None
    text_length: int
    is_duplicate: bool


@dataclass
class DocumentUploadResponse:
    """Response data for document upload."""

    message: str
    document: DocumentResponse
    text_length: int | None = None

    def to_dict(self) -> dict[str, str | dict[str, str | int | None] | int | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message": self.message,
            "document": self.document.to_dict(),
            "text_length": self.text_length,
        }


@dataclass
class DocumentListResponse:
    """Response data for listing documents."""

    documents: list[DocumentResponse]
    count: int
    total: int

    def to_dict(self) -> dict[str, list[dict[str, str | int | None]] | int]:
        """Convert to dictionary for JSON serialization."""
        return {
            "documents": [doc.to_dict() for doc in self.documents],
            "count": self.count,
            "total": self.total,
        }
