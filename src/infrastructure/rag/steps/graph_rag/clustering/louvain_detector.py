"""Louvain algorithm-based community detection implementation.

This module provides community detection using the Louvain algorithm,
a popular method for finding communities in large networks.
"""

import hashlib
from typing import Optional

try:
    import networkx as nx
    from networkx.algorithms import community as nx_community

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.clustering.base import CommunityDetector
from src.infrastructure.types.graph import Community, CommunityMetadata

logger = create_logger(__name__)


class LouvainDetector(CommunityDetector):
    """Community detection using the Louvain algorithm.

    The Louvain algorithm is a greedy optimization method for modularity-based
    community detection in large networks.
    """

    def __init__(
        self,
        resolution: float = 1.0,
        min_community_size: int = 3,
        llm_provider: Optional[LlmProvider] = None,
    ):
        """Initialize Louvain community detector.

        Args:
            resolution: Resolution parameter for community detection (higher = more communities)
            min_community_size: Minimum size for a community to be included
            llm_provider: Optional LLM provider for generating community summaries

        Raises:
            ImportError: If networkx is not installed
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError(
                "Louvain community detection requires networkx. "
                "Install with: pip install networkx"
            )

        self.resolution = resolution
        self.min_community_size = min_community_size
        self.llm_provider = llm_provider

        logger.info(f"Initialized Louvain detector with resolution={resolution}")

    def detect_communities(self, graph_store: GraphStore, workspace_id: str) -> list[Community]:
        """Detect communities using the Louvain algorithm."""
        # Export the graph from the graph store
        entities, relationships = graph_store.export_subgraph(workspace_id)

        if not entities or not relationships:
            logger.warning("Empty graph, no communities to detect")
            return []

        # Build NetworkX graph from entities and relationships
        graph = self._build_networkx_graph(entities, relationships)

        if graph.number_of_nodes() == 0:
            logger.warning("Graph has no nodes")
            return []

        # Run Louvain algorithm
        try:
            communities_generator = nx_community.louvain_communities(
                graph,
                resolution=self.resolution,
                seed=42,  # For reproducibility
            )
            community_sets = list(communities_generator)
        except Exception as e:
            logger.error(f"Louvain algorithm failed: {e}")
            return []

        # Convert to Community objects
        communities = self._sets_to_communities(community_sets, graph, workspace_id)

        # Filter by minimum size
        communities = [c for c in communities if len(c.entity_ids) >= self.min_community_size]

        # Sort by score (community size as proxy)
        communities.sort(key=lambda c: c.score, reverse=True)

        logger.info(f"Detected {len(communities)} communities using Louvain algorithm")
        return communities

    def generate_summary(self, community: Community, graph_store: GraphStore) -> str:
        """Generate a summary for a community."""
        # Get entities in the community
        entity_texts = []
        for entity_id in community.entity_ids[:10]:  # Limit to first 10 entities
            entity = graph_store.get_entity_by_id(entity_id, community.workspace_id)
            if entity:
                entity_texts.append(entity.text)

        if not entity_texts:
            return "Empty community"

        # If LLM provider is available, use it for summary generation
        if self.llm_provider:
            return self._generate_llm_summary(entity_texts, community)
        else:
            return self._generate_heuristic_summary(entity_texts, community)

    def _build_networkx_graph(self, entities, relationships) -> nx.Graph:
        """Build a NetworkX Graph from entities and relationships.

        Args:
            entities: List of Entity objects
            relationships: List of Relationship objects

        Returns:
            NetworkX Graph object
        """
        # Create graph
        graph = nx.Graph()

        # Add nodes
        for entity in entities:
            graph.add_node(entity.id, text=entity.text, type=entity.type.value)

        # Add edges with weights
        for rel in relationships:
            graph.add_edge(
                rel.source_entity_id,
                rel.target_entity_id,
                weight=rel.confidence,
                type=rel.relation_type.value,
            )

        return graph

    def _sets_to_communities(
        self, community_sets: list[set], graph: nx.Graph, workspace_id: str
    ) -> list[Community]:
        """Convert Louvain community sets to Community objects.

        Args:
            community_sets: List of sets of node IDs
            graph: NetworkX graph
            workspace_id: Workspace identifier

        Returns:
            List of Community objects
        """
        communities = []

        for idx, node_set in enumerate(community_sets):
            entity_ids = list(node_set)

            # Generate deterministic community ID
            sorted_entity_ids = sorted(entity_ids)
            combined = f"{workspace_id}|0|{'|'.join(sorted_entity_ids[:5])}"
            comm_id = hashlib.sha256(combined.encode()).hexdigest()[:16]

            # Calculate modularity for this community's subgraph
            subgraph = graph.subgraph(node_set)
            # Use community size and density as score
            density = nx.density(subgraph) if subgraph.number_of_nodes() > 1 else 0.0
            score = len(entity_ids) * density

            # Create metadata
            metadata: CommunityMetadata = {
                "detection_algorithm": "louvain",
                "resolution": self.resolution,
                "modularity": score,  # Using score as modularity proxy
            }

            community = Community(
                id=comm_id,
                workspace_id=workspace_id,
                entity_ids=entity_ids,
                level=0,
                summary="",  # Will be generated later if needed
                score=score,
                metadata=metadata,
            )
            communities.append(community)

        return communities

    def _generate_llm_summary(self, entity_texts: list[str], community: Community) -> str:
        """Generate community summary using LLM.

        Args:
            entity_texts: List of entity text strings
            community: Community object

        Returns:
            Generated summary
        """
        entities_str = ", ".join(entity_texts)
        prompt = f"""Summarize what this community of related entities represents in 1-2 sentences:

Entities: {entities_str}

Summary:"""

        try:
            if self.llm_provider is None:
                return self._generate_heuristic_summary(entity_texts, community)
            summary = self.llm_provider.generate_response(prompt)
            return summary.strip()
        except Exception as e:
            logger.warning(f"Failed to generate LLM summary: {e}")
            return self._generate_heuristic_summary(entity_texts, community)

    def _generate_heuristic_summary(self, entity_texts: list[str], community: Community) -> str:
        """Generate community summary using heuristics.

        Args:
            entity_texts: List of entity text strings
            community: Community object

        Returns:
            Generated summary
        """
        if len(entity_texts) == 0:
            return "Empty community"

        # Simple heuristic: list the entities
        if len(entity_texts) <= 5:
            return f"Community of {', '.join(entity_texts)}"
        else:
            first_five = ", ".join(entity_texts[:5])
            return f"Community of {first_five} and {len(entity_texts) - 5} other entities"
