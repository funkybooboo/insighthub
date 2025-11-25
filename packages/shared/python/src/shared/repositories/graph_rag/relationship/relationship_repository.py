"""Relationship repository interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from shared.models.relationship import Relationship


class RelationshipRepository(ABC):
    """Interface for Relationship repository operations."""

    @abstractmethod
    def create(
        self,
        workspace_id: int,
        source_entity_id: int,
        target_entity_id: int,
        relationship_type: str,
        confidence_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """
        Create a new relationship.

        Args:
            workspace_id: Workspace ID
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
            confidence_score: Confidence score (0.0 to 1.0)
            metadata: Optional metadata dictionary

        Returns:
            Created relationship
        """
        pass

    @abstractmethod
    def get_by_id(self, relationship_id: int) -> Optional[Relationship]:
        """
        Get relationship by ID.

        Args:
            relationship_id: Relationship ID

        Returns:
            Relationship if found, None if not found
        """
        pass

    @abstractmethod
    def get_by_workspace(self, workspace_id: int, skip: int = 0, limit: int = 50) -> List[Relationship]:
        """
        Get relationships by workspace ID with pagination.

        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of relationships
        """
        pass

    @abstractmethod
    def get_by_entity(self, entity_id: int, skip: int = 0, limit: int = 50) -> List[Relationship]:
        """
        Get relationships involving a specific entity.

        Args:
            entity_id: Entity ID (as source or target)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of relationships
        """
        pass

    @abstractmethod
    def get_by_type(self, workspace_id: int, relationship_type: str, skip: int = 0, limit: int = 50) -> List[Relationship]:
        """
        Get relationships by type within a workspace.

        Args:
            workspace_id: Workspace ID
            relationship_type: Relationship type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of relationships
        """
        pass

    @abstractmethod
    def update(self, relationship_id: int, **kwargs: Any) -> Optional[Relationship]:
        """
        Update relationship fields.

        Args:
            relationship_id: Relationship ID
            **kwargs: Fields to update

        Returns:
            Relationship if found and updated, None if not found
        """
        pass

    @abstractmethod
    def delete(self, relationship_id: int) -> bool:
        """
        Delete relationship by ID.

        Args:
            relationship_id: Relationship ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def count_by_workspace(self, workspace_id: int) -> int:
        """
        Count relationships in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of relationships
        """
        pass

    @abstractmethod
    def delete_by_workspace(self, workspace_id: int) -> int:
        """
        Delete all relationships in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of relationships deleted
        """
        pass