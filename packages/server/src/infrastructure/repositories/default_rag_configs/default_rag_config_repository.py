"""Default RAG configuration repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.infrastructure.models import DefaultRagConfig


class DefaultRagConfigRepository(ABC):
    """Interface for DefaultRagConfig repository operations."""

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[DefaultRagConfig]:
        """Get default RAG config for a users."""
        pass

    @abstractmethod
    def create(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Create a new default RAG config."""
        pass

    @abstractmethod
    def update(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Update an existing default RAG config."""
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> bool:
        """Delete default RAG config for a users."""
        pass