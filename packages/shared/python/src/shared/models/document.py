"""Document model."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Document:
    """Document model for storing uploaded documents."""

    id: int
    user_id: int
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    content_hash: str  # SHA-256 hash
    workspace_id: int | None = None
    chunk_count: int | None = None
    rag_collection: str | None = None  # Vector store collection name
    processing_status: str = "pending"  # 'pending', 'processing', 'ready', 'failed'
    processing_error: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, user_id={self.user_id})>"
