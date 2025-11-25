"""Entity model for Graph RAG."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class Entity:
    """Entity model for storing extracted entities from documents."""

    workspace_id: int
    document_id: int
    chunk_id: str
    entity_type: str  # 'PERSON', 'ORG', 'GPE', 'MISC', etc.
    entity_text: str
    confidence_score: float
    id: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, text='{self.entity_text}', type='{self.entity_type}', confidence={self.confidence_score})>"