"""Default RAG configuration service."""

from typing import Optional

from src.infrastructure.models import DefaultRagConfig, DefaultVectorRagConfig, DefaultGraphRagConfig
from src.infrastructure.repositories.default_rag_configs import DefaultRagConfigRepository


class DefaultRagConfigService:
    """Service for managing default RAG configurations."""

    def __init__(self, repository: DefaultRagConfigRepository):
        """
        Initialize the service.

        Args:
            repository: Repository for default RAG configs
        """
        self.repository = repository

    def get_user_config(self, user_id: int) -> Optional[DefaultRagConfig]:
        """
        Get default RAG config for a users.

        Args:
            user_id: User ID

        Returns:
            DefaultRagConfig if found, None otherwise
        """
        return self.repository.get_by_user_id(user_id)

    def create_or_update_config(
        self,
        user_id: int,
        vector_config: dict | None = None,
        graph_config: dict | None = None,
    ) -> DefaultRagConfig:
        """
        Create or update default RAG config for a users.

        Args:
            user_id: User ID
            vector_config: Vector RAG configuration
            graph_config: Graph RAG configuration

        Returns:
            Created or updated config
        """
        existing_config = self.repository.get_by_user_id(user_id)

        if existing_config:
            # Update existing config
            if vector_config:
                for key, value in vector_config.items():
                    if hasattr(existing_config.vector_config, key):
                        setattr(existing_config.vector_config, key, value)
            if graph_config:
                for key, value in graph_config.items():
                    if hasattr(existing_config.graph_config, key):
                        setattr(existing_config.graph_config, key, value)

            return self.repository.update(existing_config)
        else:
            # Create new config
            vector_cfg = DefaultVectorRagConfig()
            if vector_config:
                for key, value in vector_config.items():
                    if hasattr(vector_cfg, key):
                        setattr(vector_cfg, key, value)

            graph_cfg = DefaultGraphRagConfig()
            if graph_config:
                for key, value in graph_config.items():
                    if hasattr(graph_cfg, key):
                        setattr(graph_cfg, key, value)

            new_config = DefaultRagConfig(
                id=0,
                user_id=user_id,
                vector_config=vector_cfg,
                graph_config=graph_cfg,
            )
            return self.repository.create(new_config)

    def delete_config(self, user_id: int) -> bool:
        """
        Delete default RAG config for a users.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False otherwise
        """
        return self.repository.delete_by_user_id(user_id)
