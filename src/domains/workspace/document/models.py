"""Document model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional


class DocumentStatus(str, Enum):
    """Document processing status."""

    UPLOADED = "uploaded"
    PARSING = "parsing"
    INDEXED = "indexed"
    READY = "ready"
    FAILED = "failed"


@dataclass
class Document:
    """Represents a document in a workspace."""

    id: int
    workspace_id: int
    filename: str
    file_size: int
    mime_type: str
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Additional fields from DB
    file_path: str | None = None  # Maps to storage_path in DB
    content_hash: str | None = None  # Maps to file_hash in DB
    original_filename: str | None = None

    # Additional fields for domain logic (not in DB)
    rag_collection: str | None = None  # Vector store collection name
    parsed_text: str | None = None  # Extracted text content

    def __repr__(self) -> str:
        return (
            f"<Document(id={self.id}, filename={self.filename}, workspace_id={self.workspace_id})>"
        )
