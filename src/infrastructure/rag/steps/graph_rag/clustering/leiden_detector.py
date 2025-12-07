"""Leiden algorithm-based community detection implementation.

This module provides community detection using the Leiden algorithm,
which is an improved version of the Louvain algorithm.
"""

import hashlib
from typing import Optional

try:
    import igraph as ig
    import leidenalg

    LEIDEN_AVAILABLE = True
except ImportError:
    LEIDEN_AVAILABLE = False

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.clustering.base import CommunityDetector
from src.infrastructure.types.graph import Community, CommunityMetadata

logger = create_logger(__name__)


class LeidenDetector(CommunityDetector):
    """Community detection using the Leiden algorithm.

    The Leiden algorithm is a hierarchical community detection method that
    finds densely connected groups of nodes in a network. It improves upon
    the Louvain algorithm by addressing some of its quality issues.
    """

    def __init__(
        self,
        resolution: float = 1.0,
        max_level: int = 3,
        min_community_size: int = 3,
        llm_provider: Optional[LlmProvider] = None,
    ):
        """Initialize Leiden community detector.

        Args:
            resolution: Resolution parameter for community detection (higher = more communities)
            max_level: Maximum level for hierarchical clustering
            min_community_size: Minimum size for a community to be included
            llm_provider: Optional LLM provider for generating community summaries

        Raises:
            ImportError: If python-igraph or leidenalg are not installed
        """
        if not LEIDEN_AVAILABLE:
            raise ImportError(
                "Leiden community detection requires python-igraph and leidenalg. "
                "Install with: pip install python-igraph leidenalg"
            )

        self.resolution = resolution
        self.max_level = max_level
        self.min_community_size = min_community_size
        self.llm_provider = llm_provider

        logger.info(
            f"Initialized Leiden detector with resolution={resolution}, max_level={max_level}"
        )

    def detect_communities(self, graph_store: GraphStore, workspace_id: str) -> list[Community]:
        """Detect communities using the Leiden algorithm."""
        # Export the graph from the graph store
        entities, relationships = graph_store.export_subgraph(workspace_id)

        if not entities or not relationships:
            logger.warning("Empty graph, no communities to detect")
            return []

        # Build igraph from entities and relationships
        graph = self._build_igraph(entities, relationships)

        if graph.vcount() == 0:
            logger.warning("Graph has no vertices")
            return []

        # Run Leiden algorithm
        try:
            partition = leidenalg.find_partition(
                graph,
                leidenalg.RBConfigurationVertexPartition,
                resolution_parameter=self.resolution,
                n_iterations=-1,  # Run until convergence
            )
        except Exception as e:
            logger.error(f"Leiden algorithm failed: {e}")
            return []

        # Convert partition to Community objects
        communities = self._partition_to_communities(partition, entities, workspace_id, level=0)

        # Filter by minimum size
        communities = [c for c in communities if len(c.entity_ids) >= self.min_community_size]

        # Sort by score (modularity contribution)
        communities.sort(key=lambda c: c.score, reverse=True)

        logger.info(f"Detected {len(communities)} communities using Leiden algorithm")
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

    def _build_igraph(self, entities, relationships) -> ig.Graph:
        """Build an igraph Graph from entities and relationships.

        Args:
            entities: List of Entity objects
            relationships: List of Relationship objects

        Returns:
            igraph Graph object
        """
        # Create vertex mapping
        entity_id_to_index = {entity.id: idx for idx, entity in enumerate(entities)}

        # Create graph
        graph = ig.Graph(n=len(entities))

        # Add vertex names
        graph.vs["name"] = [entity.id for entity in entities]
        graph.vs["text"] = [entity.text for entity in entities]

        # Add edges
        edges = []
        weights = []
        for rel in relationships:
            source_idx = entity_id_to_index.get(rel.source_entity_id)
            target_idx = entity_id_to_index.get(rel.target_entity_id)

            if source_idx is not None and target_idx is not None:
                edges.append((source_idx, target_idx))
                weights.append(rel.confidence)

        if edges:
            graph.add_edges(edges)
            graph.es["weight"] = weights

        return graph

    def _partition_to_communities(
        self, partition, entities, workspace_id: str, level: int
    ) -> list[Community]:
        """Convert igraph partition to Community objects.

        Args:
            partition: Leiden partition result
            entities: List of Entity objects
            workspace_id: Workspace identifier
            level: Hierarchical level of communities

        Returns:
            List of Community objects
        """
        communities = []

        # Group entity IDs by community
        community_members: dict[int, list[str]] = {}
        for idx, community_id in enumerate(partition.membership):
            if community_id not in community_members:
                community_members[community_id] = []
            community_members[community_id].append(entities[idx].id)

        # Create Community objects
        for community_id, entity_ids in community_members.items():
            # Generate deterministic community ID
            sorted_entity_ids = sorted(entity_ids)
            combined = f"{workspace_id}|{level}|{'|'.join(sorted_entity_ids[:5])}"
            comm_id = hashlib.sha256(combined.encode()).hexdigest()[:16]

            # Calculate community score (use modularity if available)
            score = partition.modularity if hasattr(partition, "modularity") else 0.0

            # Create metadata
            metadata: CommunityMetadata = {
                "detection_algorithm": "leiden",
                "resolution": self.resolution,
                "modularity": partition.modularity if hasattr(partition, "modularity") else 0.0,
            }

            community = Community(
                id=comm_id,
                workspace_id=workspace_id,
                entity_ids=entity_ids,
                level=level,
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
