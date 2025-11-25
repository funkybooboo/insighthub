"""Community repository interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from shared.models.community import Community


class CommunityRepository(ABC):
    """Interface for Community repository operations."""

    @abstractmethod
    def create(
        self,
        workspace_id: int,
        community_id: str,
        entity_ids: List[int],
        algorithm_used: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Community:
        """
        Create a new community.

        Args:
            workspace_id: Workspace ID
            community_id: Unique community identifier
            entity_ids: List of entity IDs in this community
            algorithm_used: Algorithm used for community detection
            metadata: Optional metadata dictionary

        Returns:
            Created community
        """
        pass

    @abstractmethod
    def get_by_id(self, community_id: int) -> Optional[Community]:
        """
        Get community by ID.

        Args:
            community_id: Community ID

        Returns:
            Community if found, None if not found
        """
        pass

    @abstractmethod
    def get_by_workspace(self, workspace_id: int, skip: int = 0, limit: int = 50) -> List[Community]:
        """
        Get communities by workspace ID with pagination.

        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of communities
        """
        pass

    @abstractmethod
    def get_by_community_id(self, workspace_id: int, community_id: str) -> Optional[Community]:
        """
        Get community by community_id within a workspace.

        Args:
            workspace_id: Workspace ID
            community_id: Community identifier

        Returns:
            Community if found, None if not found
        """
        pass

    @abstractmethod
    def get_by_algorithm(self, workspace_id: int, algorithm_used: str, skip: int = 0, limit: int = 50) -> List[Community]:
        """
        Get communities by algorithm within a workspace.

        Args:
            workspace_id: Workspace ID
            algorithm_used: Algorithm to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of communities
        """
        pass

    @abstractmethod
    def update(self, community_id: int, **kwargs: Any) -> Optional[Community]:
        """
        Update community fields.

        Args:
            community_id: Community ID
            **kwargs: Fields to update

        Returns:
            Community if found and updated, None if not found
        """
        pass

    @abstractmethod
    def delete(self, community_id: int) -> bool:
        """
        Delete community by ID.

        Args:
            community_id: Community ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def count_by_workspace(self, workspace_id: int) -> int:
        """
        Count communities in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of communities
        """
        pass

    @abstractmethod
    def delete_by_workspace(self, workspace_id: int) -> int:
        """
        Delete all communities in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of communities deleted
        """
        pass