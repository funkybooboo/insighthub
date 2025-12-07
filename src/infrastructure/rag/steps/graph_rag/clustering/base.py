"""Base interface for community detection in Graph RAG.

This module defines the abstract interface for detecting communities (clusters)
of related entities in knowledge graphs.
"""

from abc import ABC, abstractmethod

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.types.graph import Community


class CommunityDetector(ABC):
    """Abstract base class for community detection algorithms.

    Implementations should detect communities (densely connected groups of entities)
    in the knowledge graph and optionally generate summaries for each community.
    """

    @abstractmethod
    def detect_communities(self, graph_store: GraphStore, workspace_id: str) -> list[Community]:
        """Detect communities in the graph.

        Args:
            graph_store: Graph store containing the entities and relationships
            workspace_id: Workspace identifier for data isolation

        Returns:
            List of detected communities

        Note:
            Communities should be ordered by score (highest first).
            Each community should have a unique ID within the workspace.
        """
        pass

    @abstractmethod
    def generate_summary(self, community: Community, graph_store: GraphStore) -> str:
        """Generate a summary for a community.

        Args:
            community: Community to summarize
            graph_store: Graph store to retrieve entity/relationship details

        Returns:
            Human-readable summary of the community

        Note:
            This may use LLMs or heuristic methods to generate summaries.
            The summary should describe what the community represents.
        """
        pass
