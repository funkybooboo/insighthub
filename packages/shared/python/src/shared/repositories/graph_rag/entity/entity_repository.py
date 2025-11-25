"""Entity repository interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from shared.models.entity import Entity


class EntityRepository(ABC):
    """Interface for Entity repository operations."""

    @abstractmethod
    def create(
        self,
        workspace_id: int,
        document_id: int,
        chunk_id: str,
        entity_type: str,
        entity_text: str,
        confidence_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """
        Create a new entity.

        Args:
            workspace_id: Workspace ID
            document_id: Document ID
            chunk_id: Chunk identifier
            entity_type: Type of entity (PERSON, ORG, etc.)
            entity_text: The entity text
            confidence_score: Confidence score (0.0 to 1.0)
            metadata: Optional metadata dictionary

        Returns:
            Created entity
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Entity]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity if found, None if not found
        """
        pass

    @abstractmethod
    def get_by_workspace(self, workspace_id: int, skip: int = 0, limit: int = 50) -> List[Entity]:
        """
        Get entities by workspace ID with pagination.

        Args:
            workspace_id: Workspace ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    def get_by_document(self, document_id: int, skip: int = 0, limit: int = 50) -> List[Entity]:
        """
        Get entities by document ID with pagination.

        Args:
            document_id: Document ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    def get_by_chunk(self, chunk_id: str) -> List[Entity]:
        """
        Get entities by chunk ID.

        Args:
            chunk_id: Chunk identifier

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    def get_by_type(self, workspace_id: int, entity_type: str, skip: int = 0, limit: int = 50) -> List[Entity]:
        """
        Get entities by type within a workspace.

        Args:
            workspace_id: Workspace ID
            entity_type: Entity type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    def update(self, entity_id: int, **kwargs: Any) -> Optional[Entity]:
        """
        Update entity fields.

        Args:
            entity_id: Entity ID
            **kwargs: Fields to update

        Returns:
            Entity if found and updated, None if not found
        """
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Delete entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def count_by_workspace(self, workspace_id: int) -> int:
        """
        Count entities in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of entities
        """
        pass

    @abstractmethod
    def delete_by_workspace(self, workspace_id: int) -> int:
        """
        Delete all entities in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of entities deleted
        """
        pass