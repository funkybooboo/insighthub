"""Document model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Document:
    """Document model for storing uploaded documents."""

    id: int
    workspace_id: int
    filename: str
    file_size: int
    mime_type: str
    chunk_count: int = 0
    processing_status: str = "processing"  # 'processing', 'ready', 'failed'
    processing_error: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Additional fields for domain logic (not in DB)
    file_path: str | None = None  # Local file path
    content_hash: str | None = None  # SHA-256 hash
    rag_collection: str | None = None  # Vector store collection name
    parsed_text: str | None = None  # Extracted text content

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, workspace_id={self.workspace_id})>"