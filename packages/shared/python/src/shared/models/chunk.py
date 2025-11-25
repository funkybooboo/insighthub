"""Chunk model for document chunks."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class Chunk:
    """Chunk model for storing document text chunks."""

    document_id: int
    chunk_index: int
    chunk_text: str
    id: Optional[UUID] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index}, text_len={len(self.chunk_text)})>"

    @property
    def chunk_id(self) -> str:
        """Generate a chunk identifier for use in entity relationships."""
        return f"{self.document_id}_{self.chunk_index}"