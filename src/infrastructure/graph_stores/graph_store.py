"""Base interface for graph stores.

This module defines the abstract interface for graph storage backends used in
Graph RAG. Implementations should handle entity and relationship storage,
graph traversal, and community management.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.infrastructure.types.graph import Community, Entity, GraphSubgraph, Relationship


class GraphStore(ABC):
    """Abstract base class for graph storage backends.

    This interface defines the contract for storing and querying knowledge graphs
    used in Graph RAG. Implementations should ensure thread-safety and proper
    error handling.
    """

    @abstractmethod
    def upsert_entities(self, entities: list[Entity], workspace_id: str) -> None:
        """Upsert entities into the graph store.

        Args:
            entities: List of entities to upsert, with proper EntityType enum values
            workspace_id: Workspace identifier for data isolation

        Note:
            If an entity with the same ID exists, it should be updated.
            The implementation should merge document_ids if the entity exists.
        """
        pass

    @abstractmethod
    def upsert_relationships(self, relationships: list[Relationship], workspace_id: str) -> None:
        """Upsert relationships into the graph store.

        Args:
            relationships: List of relationships to upsert, with proper RelationType enum values
            workspace_id: Workspace identifier for data isolation

        Note:
            If a relationship with the same ID exists, it should be updated.
        """
        pass

    @abstractmethod
    def upsert_communities(self, communities: list[Community], workspace_id: str) -> None:
        """Upsert communities into the graph store.

        Args:
            communities: List of communities to upsert
            workspace_id: Workspace identifier for data isolation

        Note:
            If a community with the same ID exists, it should be updated.
            Communities should be linked to their member entities.
        """
        pass

    @abstractmethod
    def get_entity_by_id(self, entity_id: str, workspace_id: str) -> Optional[Entity]:
        """Retrieve a single entity by its ID.

        Args:
            entity_id: Unique identifier of the entity
            workspace_id: Workspace identifier for data isolation

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_entities(self, query: str, workspace_id: str, limit: int) -> list[Entity]:
        """Find entities matching the query string.

        Args:
            query: Search query string (implementation-specific matching)
            workspace_id: Workspace identifier for data isolation
            limit: Maximum number of entities to return

        Returns:
            List of matching entities, sorted by relevance
        """
        pass

    @abstractmethod
    def traverse_graph(
        self, entity_ids: list[str], workspace_id: str, max_depth: int
    ) -> GraphSubgraph:
        """Traverse the graph from starting entities up to max_depth.

        Args:
            entity_ids: Starting entity IDs for traversal
            workspace_id: Workspace identifier for data isolation
            max_depth: Maximum depth for graph traversal

        Returns:
            GraphSubgraph containing all entities and relationships within max_depth
        """
        pass

    @abstractmethod
    def get_communities(self, entity_ids: list[str], workspace_id: str) -> list[Community]:
        """Get communities associated with the given entities.

        Args:
            entity_ids: Entity IDs to find communities for
            workspace_id: Workspace identifier for data isolation

        Returns:
            List of communities that contain any of the given entities
        """
        pass

    @abstractmethod
    def delete_document_graph(self, document_id: str, workspace_id: str) -> None:
        """Delete all entities and relationships associated with a document.

        Args:
            document_id: Document identifier
            workspace_id: Workspace identifier for data isolation

        Note:
            This should remove the document_id from entity metadata and delete
            relationships that only exist in this document.
        """
        pass

    @abstractmethod
    def delete_workspace_graph(self, workspace_id: str) -> None:
        """Delete all entities, relationships, and communities for a workspace.

        Args:
            workspace_id: Workspace identifier for data isolation

        Note:
            This should completely remove all graph data associated with the workspace.
            Used during workspace deletion.
        """
        pass

    @abstractmethod
    def create_constraint(self, label: str, property: str) -> None:
        """Create a uniqueness constraint on a node label property.

        Args:
            label: Node label (e.g., "Entity", "Community")
            property: Property name to constrain (e.g., "id")

        Note:
            Implementation should be idempotent (no error if constraint exists).
        """
        pass

    @abstractmethod
    def create_index(self, label: str, properties: list[str]) -> None:
        """Create an index on node label properties.

        Args:
            label: Node label (e.g., "Entity", "Community")
            properties: Property names to index

        Note:
            Implementation should be idempotent (no error if index exists).
        """
        pass

    @abstractmethod
    def export_subgraph(self, workspace_id: str) -> tuple[list[Entity], list[Relationship]]:
        """Export the entire graph for a workspace.

        Args:
            workspace_id: Workspace identifier for data isolation

        Returns:
            Tuple of (entities, relationships) for the entire workspace graph
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connections and clean up resources.

        Note:
            Should be called when the graph store is no longer needed.
        """
        pass
