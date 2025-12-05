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
        vector_config: dict | None = None,
        graph_config: dict | None = None,
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
            logger.info("Updating existing RAG config")
            # Update existing config
            existing_config.rag_type = rag_type
            if vector_config:
                for key, value in vector_config.items():
                    if hasattr(existing_config.vector_config, key):
                        setattr(existing_config.vector_config, key, value)
            if graph_config:
                for key, value in graph_config.items():
                    if hasattr(existing_config.graph_config, key):
                        setattr(existing_config.graph_config, key, value)

            updated_config = self.data_access.update(existing_config)
            logger.info("RAG config updated")
            return updated_config
        else:
            logger.info("Creating new RAG config")
            # Create new config (should only happen once on first run)
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
                id=1,  # Always id=1 for single-row table
                rag_type=rag_type,
                vector_config=vector_cfg,
                graph_config=graph_cfg,
            )
            updated_config = self.data_access.update(new_config)
            logger.info("RAG config created")
            return updated_config
