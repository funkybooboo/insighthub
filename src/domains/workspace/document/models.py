"""Document model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Document:
    """Document model for storing uploaded document."""

    id: int
    workspace_id: int
    filename: str
    file_size: int  # Maps to size_bytes in DB
    mime_type: str
    chunk_count: int = 0
    status: str = "pending"  # 'pending', 'processing', 'ready', 'failed'
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

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
