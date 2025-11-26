"""Default RAG configuration service."""

from typing import Optional

from src.infrastructure.logger import create_logger
from src.infrastructure.models import (
    DefaultGraphRagConfig,
    DefaultRagConfig,
    DefaultVectorRagConfig,
)
from src.infrastructure.repositories.default_rag_configs import DefaultRagConfigRepository

logger = create_logger(__name__)


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
        logger.info(f"Creating/updating default RAG config: user_id={user_id}")

        existing_config = self.repository.get_by_user_id(user_id)

        if existing_config:
            logger.info(f"Updating existing RAG config: user_id={user_id}")
            # Update existing config
            if vector_config:
                for key, value in vector_config.items():
                    if hasattr(existing_config.vector_config, key):
                        setattr(existing_config.vector_config, key, value)
            if graph_config:
                for key, value in graph_config.items():
                    if hasattr(existing_config.graph_config, key):
                        setattr(existing_config.graph_config, key, value)

            updated_config = self.repository.update(existing_config)
            logger.info(f"RAG config updated: user_id={user_id}")
            return updated_config
        else:
            logger.info(f"Creating new RAG config: user_id={user_id}")
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
            created_config = self.repository.create(new_config)
            logger.info(f"RAG config created: user_id={user_id}")
            return created_config

    def delete_config(self, user_id: int) -> bool:
        """
        Delete default RAG config for a users.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting default RAG config: user_id={user_id}")

        deleted = self.repository.delete_by_user_id(user_id)

        if deleted:
            logger.info(f"RAG config deleted: user_id={user_id}")
        else:
            logger.warning(f"RAG config deletion failed: config not found (user_id={user_id})")

        return deleted
