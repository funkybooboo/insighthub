"""Graph data types for Graph RAG."""

from dataclasses import dataclass
from typing import Any


@dataclass
class GraphNode:
    """
    Graph node representation (normalized schema-level type).

    Implementations may map this to DB-specific node objects (Neo4j, ArangoDB, etc.).

    Attributes:
        id: Unique node identifier
        labels: List of node labels/types (e.g., ['Entity', 'Person'])
        properties: Node properties dictionary
    """

    id: str
    labels: list[str]
    properties: dict[str, Any]


@dataclass
class GraphEdge:
    """
    Graph edge representation connecting two nodes.

    Attributes:
        id: Unique edge identifier
        source: Source node ID
        target: Target node ID
        label: Edge type/relationship label
        properties: Edge properties dictionary
    """

    id: str
    source: str
    target: str
    label: str
    properties: dict[str, Any]
