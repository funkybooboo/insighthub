"""Community model for Graph RAG."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Community:
    """Community model for storing detected communities/clusters of entities."""

    workspace_id: int
    community_id: str  # Unique identifier for the community
    entity_ids: List[int]  # List of entity IDs in this community
    algorithm_used: str  # 'leiden', 'louvain', etc.
    id: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Community(id={self.id}, community_id='{self.community_id}', entities={len(self.entity_ids)}, algorithm='{self.algorithm_used}')>"