"""Relationship model for Graph RAG."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class Relationship:
    """Relationship model for storing extracted relationships between entities."""

    workspace_id: int
    source_entity_id: int
    target_entity_id: int
    relationship_type: str  # 'WORKS_FOR', 'LOCATED_IN', 'PART_OF', etc.
    confidence_score: float
    id: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Relationship(id={self.id}, type='{self.relationship_type}', source={self.source_entity_id}, target={self.target_entity_id}, confidence={self.confidence_score})>"