"""Query-related event schemas."""

from dataclasses import dataclass
from typing import Any


@dataclass
class QueryPrepareEvent:
    """
    Published to trigger query context preparation.

    Consumed by: Query Worker
    """

    query_id: str
    workspace_id: str
    query_text: str
    rag_type: str  # 'vector', 'graph', 'hybrid'
    top_k: int
    metadata: dict[str, Any]


@dataclass
class QueryReadyEvent:
    """
    Published when query context is prepared and cached.

    Consumed by: Server
    """

    query_id: str
    workspace_id: str
    context_key: str  # Redis cache key
    chunk_count: int
    metadata: dict[str, Any]
