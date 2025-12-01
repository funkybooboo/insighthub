"""In-memory implementation of DefaultRagConfigRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.models import DefaultRagConfig

from .default_rag_config_repository import DefaultRagConfigRepository


class InMemoryDefaultRagConfigRepository(DefaultRagConfigRepository):
    """In-memory implementation of DefaultRagConfigRepository for development/testing."""

    def __init__(self):
        """Initialize the repository."""
        self._configs: dict[int, DefaultRagConfig] = {}
        self._next_id = 1

    def get_by_user_id(self, user_id: int) -> Optional[DefaultRagConfig]:
        """Get default RAG config for a users."""
        for config in self._configs.values():
            if config.user_id == user_id:
                return config
        return None

    def create(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Create a new default RAG config."""
        config.id = self._next_id
        config.created_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        self._configs[self._next_id] = config
        self._next_id += 1
        return config

    def update(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Update an existing default RAG config."""
        if config.id not in self._configs:
            raise ValueError(f"Config with id {config.id} not found")

        config.updated_at = datetime.utcnow()
        self._configs[config.id] = config
        return config

    def delete_by_user_id(self, user_id: int) -> bool:
        """Delete default RAG config for a users."""
        for config_id, config in list(self._configs.items()):
            if config.user_id == user_id:
                del self._configs[config_id]
                return True
        return False
