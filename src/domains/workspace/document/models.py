"""Document model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Fine-grained document processing statuses."""

    # Initial state
    PENDING = "pending"  # Document uploaded, waiting to start processing

    # Upload/Storage phase
    UPLOADING = "uploading"  # Uploading to blob storage
    UPLOADED = "uploaded"  # Successfully uploaded to blob storage

    # Processing phase
    PARSING = "parsing"  # Extracting text from document
    PARSED = "parsed"  # Text extraction complete
    CHUNKING = "chunking"  # Splitting text into chunks
    CHUNKED = "chunked"  # Chunking complete
    EMBEDDING = "embedding"  # Generating embeddings
    EMBEDDED = "embedded"  # Embeddings generated
    INDEXING = "indexing"  # Storing in vector database
    INDEXED = "indexed"  # Stored in vector database

    # Terminal states
    READY = "ready"  # Fully processed and searchable
    FAILED = "failed"  # Processing failed at some stage

    @classmethod
    def is_terminal(cls, status: str) -> bool:
        """Check if status is a terminal state."""
        return status in (cls.READY.value, cls.FAILED.value)

    @classmethod
    def is_processing(cls, status: str) -> bool:
        """Check if document is actively being processed."""
        return status in (
            cls.UPLOADING.value,
            cls.PARSING.value,
            cls.CHUNKING.value,
            cls.EMBEDDING.value,
            cls.INDEXING.value,
        )


@dataclass
class Document:
    """Document model for storing uploaded document."""

    id: int
    workspace_id: int
    filename: str
    file_size: int  # Maps to size_bytes in DB
    mime_type: str
    chunk_count: int = 0
    status: str = DocumentStatus.PENDING.value
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
