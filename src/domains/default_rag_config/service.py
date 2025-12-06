"""Default RAG configuration service."""

from typing import Optional

from src.domains.default_rag_config.data_access import DefaultRagConfigDataAccess
from src.domains.default_rag_config.models import (
    DefaultGraphRagConfig,
    DefaultRagConfig,
    DefaultVectorRagConfig,
)
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class DefaultRagConfigService:
    """Service for managing default RAG configuration (single-user system)."""

    def __init__(self, data_access: DefaultRagConfigDataAccess):
        """
        Initialize the service.

        Args:
            data_access: Data access layer for default RAG configs
        """
        self.data_access = data_access

    def get_config(self) -> Optional[DefaultRagConfig]:
        """
        Get the default RAG config (single row, id=1).

        Returns:
            DefaultRagConfig if found, None otherwise
        """
        return self.data_access.get()

    def create_or_update_config(
        self,
        rag_type: str = "vector",
        vector_config: Optional[dict]= None,
        graph_config: Optional[dict]= None,
    ) -> DefaultRagConfig:
        """
        Create or update default RAG config (single-user system).

        Args:
            rag_type: RAG type ("vector" or "graph")
            vector_config: Vector RAG configuration
            graph_config: Graph RAG configuration

        Returns:
            Created or updated config
        """
        logger.info("Creating/updating default RAG config")

        existing_config = self.data_access.get()

        if existing_config:
            return self._update_existing_config(existing_config, rag_type, vector_config, graph_config)

        return self._create_new_config(rag_type, vector_config, graph_config)

    def _update_existing_config(
        self,
        existing_config: DefaultRagConfig,
        rag_type: str,
        vector_config: Optional[dict],
        graph_config: Optional[dict],
    ) -> DefaultRagConfig:
        """Update existing RAG configuration."""
        logger.info("Updating existing RAG config")
        existing_config.rag_type = rag_type

        if vector_config:
            self._apply_config_updates(existing_config.vector_config, vector_config)

        if graph_config:
            self._apply_config_updates(existing_config.graph_config, graph_config)

        updated_config = self.data_access.update(existing_config)
        logger.info("RAG config updated")
        return updated_config

    def _create_new_config(
        self,
        rag_type: str,
        vector_config: Optional[dict],
        graph_config: Optional[dict],
    ) -> DefaultRagConfig:
        """Create new RAG configuration."""
        logger.info("Creating new RAG config")

        vector_cfg = DefaultVectorRagConfig()
        if vector_config:
            self._apply_config_updates(vector_cfg, vector_config)

        graph_cfg = DefaultGraphRagConfig()
        if graph_config:
            self._apply_config_updates(graph_cfg, graph_config)

        new_config = DefaultRagConfig(
            id=1,  # Always id=1 for single-row table
            rag_type=rag_type,
            vector_config=vector_cfg,
            graph_config=graph_cfg,
        )
        updated_config = self.data_access.update(new_config)
        logger.info("RAG config created")
        return updated_config

    def _apply_config_updates(self, config_obj, updates: dict) -> None:
        """Apply configuration updates to a config object."""
        for key, value in updates.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
