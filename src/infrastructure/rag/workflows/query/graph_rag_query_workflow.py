"""Graph RAG query workflow implementation.

This workflow orchestrates the full Graph RAG query process:
1. Extract entities from query
2. Find matching entities in graph
3. Traverse graph to find related entities
4. Retrieve communities
5. Return context
"""

from typing import Optional, cast

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.entity_extraction.base import EntityExtractor
from src.infrastructure.rag.workflows.query.query_workflow import QueryWorkflow, QueryWorkflowError
from src.infrastructure.types.common import FilterDict, MetadataDict
from src.infrastructure.types.rag import ChunkData

logger = create_logger(__name__)


class GraphRagQueryWorkflow(QueryWorkflow):
    """
    Graph RAG query workflow implementation.

    This workflow:
    1. Extracts entities from the query
    2. Finds matching entities in the graph
    3. Traverses the graph to find related entities
    4. Retrieves relevant communities
    5. Builds context from entities, relationships, and communities
    """

    def __init__(
        self,
        entity_extractor: EntityExtractor,
        graph_store: GraphStore,
        workspace_id: str,
        max_traversal_depth: int = 2,
        top_k_entities: int = 10,
        top_k_communities: int = 3,
        include_entity_neighborhoods: bool = True,
    ) -> None:
        """Initialize graph RAG query workflow.

        Args:
            entity_extractor: Entity extraction implementation
            graph_store: Graph store for querying
            workspace_id: Workspace identifier
            max_traversal_depth: Maximum depth for graph traversal
            top_k_entities: Number of top entities to retrieve
            top_k_communities: Number of top communities to include
            include_entity_neighborhoods: Whether to include entity neighborhoods
        """
        self.entity_extractor = entity_extractor
        self.graph_store = graph_store
        self.workspace_id = workspace_id
        self.max_traversal_depth = max_traversal_depth
        self.top_k_entities = top_k_entities
        self.top_k_communities = top_k_communities
        self.include_entity_neighborhoods = include_entity_neighborhoods

    def execute(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[FilterDict] = None,
    ) -> list[ChunkData]:
        """
        Execute Graph RAG query workflow.

        Args:
            query_text: User's query text
            top_k: Number of results to return (overrides top_k_entities if provided)
            filters: Optional filters (not used in graph RAG currently)

        Returns:
            List of relevant chunks with scores

        Raises:
            QueryWorkflowError: If any step fails
        """
        # Override top_k_entities if provided
        effective_top_k = top_k if top_k else self.top_k_entities

        # Step 1: Extract entities from query
        logger.info(f"[GraphRagQueryWorkflow] Extracting entities from query: {query_text[:50]}...")
        try:
            query_entities = self.entity_extractor.extract_entities(query_text)
            logger.info(
                f"[GraphRagQueryWorkflow] Extracted {len(query_entities)} entities from query"
            )

            if not query_entities:
                logger.warning("No entities found in query, returning empty results")
                return []

        except Exception as e:
            raise QueryWorkflowError(
                f"Failed to extract entities from query: {str(e)}",
                step="entity_extraction",
            ) from e

        # Step 2: Find matching entities in graph
        logger.info("[GraphRagQueryWorkflow] Finding matching entities in graph")
        try:
            matching_entity_ids = []
            for query_entity in query_entities:
                # Try to find exact match first
                found_entity = self.graph_store.get_entity_by_id(query_entity.id, self.workspace_id)
                if found_entity:
                    matching_entity_ids.append(found_entity.id)
                else:
                    # Fallback to text search
                    found_entities = self.graph_store.find_entities(
                        query_entity.text, self.workspace_id, limit=3
                    )
                    matching_entity_ids.extend([e.id for e in found_entities])

            # Deduplicate and limit
            matching_entity_ids = list(set(matching_entity_ids))[:effective_top_k]
            logger.info(
                f"[GraphRagQueryWorkflow] Found {len(matching_entity_ids)} matching entities"
            )

            if not matching_entity_ids:
                logger.warning("No matching entities found in graph, returning empty results")
                return []

        except Exception as e:
            raise QueryWorkflowError(
                f"Failed to find matching entities: {str(e)}",
                step="entity_matching",
            ) from e

        # Step 3: Traverse graph to find related entities
        logger.info(f"[GraphRagQueryWorkflow] Traversing graph (depth={self.max_traversal_depth})")
        try:
            subgraph = self.graph_store.traverse_graph(
                matching_entity_ids, self.workspace_id, self.max_traversal_depth
            )
            logger.info(
                f"[GraphRagQueryWorkflow] Traversed graph: {len(subgraph.entities)} entities, "
                f"{len(subgraph.relationships)} relationships"
            )

        except Exception as e:
            raise QueryWorkflowError(
                f"Failed to traverse graph: {str(e)}",
                step="graph_traversal",
            ) from e

        # Step 4: Retrieve communities
        logger.info(
            f"[GraphRagQueryWorkflow] Retrieving communities (top_k={self.top_k_communities})"
        )
        try:
            communities = self.graph_store.get_communities(matching_entity_ids, self.workspace_id)
            # Limit to top_k communities
            communities = communities[: self.top_k_communities]
            logger.info(f"[GraphRagQueryWorkflow] Retrieved {len(communities)} communities")

        except Exception as e:
            logger.warning(
                f"Failed to retrieve communities: {str(e)}, continuing without communities"
            )
            communities = []

        # Step 5: Build context from results
        logger.info("[GraphRagQueryWorkflow] Building context from results")
        try:
            chunks = []

            # Add entity context
            for entity in subgraph.entities[:effective_top_k]:
                # Build entity description with relationships
                entity_relationships = [
                    rel
                    for rel in subgraph.relationships
                    if rel.source_entity_id == entity.id or rel.target_entity_id == entity.id
                ]

                # Create context text
                context_parts = [f"Entity: {entity.text} (Type: {entity.type.value})"]

                if entity_relationships and self.include_entity_neighborhoods:
                    rel_descriptions = []
                    for rel in entity_relationships[:3]:  # Limit to 3 relationships per entity
                        # Find the other entity
                        other_entity_id = (
                            rel.target_entity_id
                            if rel.source_entity_id == entity.id
                            else rel.source_entity_id
                        )
                        other_entity = next(
                            (e for e in subgraph.entities if e.id == other_entity_id), None
                        )
                        if other_entity:
                            rel_descriptions.append(
                                f"{rel.relation_type.value} {other_entity.text}"
                            )

                    if rel_descriptions:
                        context_parts.append("Relationships: " + ", ".join(rel_descriptions))

                chunk_data = ChunkData(
                    chunk_id=entity.id,
                    document_id=entity.metadata.get("document_id", "unknown"),
                    text="\n".join(context_parts),
                    score=entity.confidence,
                    metadata=cast(MetadataDict, {**entity.metadata}),
                )
                chunks.append(chunk_data)

            # Add community summaries
            for community in communities:
                if community.summary:
                    chunk_data = ChunkData(
                        chunk_id=community.id,
                        document_id="community",
                        text=f"Community Summary: {community.summary}",
                        score=community.score,
                        metadata=cast(MetadataDict, {**community.metadata}),
                    )
                    chunks.append(chunk_data)

            # Sort by score
            chunks.sort(key=lambda c: c.score, reverse=True)

            logger.info(f"[GraphRagQueryWorkflow] Returning {len(chunks)} results")
            return chunks

        except Exception as e:
            raise QueryWorkflowError(
                f"Failed to build context: {str(e)}",
                step="build_context",
            ) from e
