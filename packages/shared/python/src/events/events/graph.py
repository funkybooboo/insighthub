"""Graph-related event schemas."""

from dataclasses import dataclass
from typing import Any


@dataclass
class GraphBuildCompleteEvent:
    """
    Published when graph construction is complete for a document.

    Consumed by: Server (for notifications), Enrichment Worker
    """

    document_id: str
    workspace_id: str
    node_count: int
    edge_count: int
    community_count: int
    metadata: dict[str, Any]
