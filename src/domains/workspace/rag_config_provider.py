"""RAG configuration provider abstraction for polymorphic config handling."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from src.config import config
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.models import GraphRagConfig, VectorRagConfig
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.options import (
    get_default_chunking_algorithm,
    get_default_clustering_algorithm,
    get_default_embedding_algorithm,
    get_default_entity_extraction_algorithm,
    get_default_relationship_extraction_algorithm,
    get_default_reranking_algorithm,
)
from src.infrastructure.types.common import WorkspaceContext

logger = create_logger(__name__)


class RagConfigProvider(ABC):
    """Abstract provider for RAG configuration.

    This abstraction eliminates conditional "if vector else graph" logic throughout
    the codebase by encapsulating RAG type-specific config building.
    """

    @abstractmethod
    def get_config_model(self, workspace_id: int) -> Optional[VectorRagConfig | GraphRagConfig]:
        """Get RAG config model for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Config model or None if not found
        """
        pass

    @abstractmethod
    def build_query_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build query workflow settings for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Query settings dict with all necessary configuration
        """
        pass

    @abstractmethod
    def build_indexing_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build indexing workflow settings for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Indexing settings dict with all necessary configuration
        """
        pass

    @abstractmethod
    def build_provisioning_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build provisioning workflow settings for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Provisioning settings dict with all necessary configuration
        """
        pass


class VectorRagConfigProvider(RagConfigProvider):
    """Provider for Vector RAG configuration."""

    def __init__(self, workspace_data_access: WorkspaceDataAccess):
        """Initialize vector RAG config provider.

        Args:
            workspace_data_access: Workspace data access layer
        """
        self.workspace_data_access = workspace_data_access

    def get_config_model(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get vector RAG config model."""
        return self.workspace_data_access.get_vector_rag_config(workspace_id)

    def build_query_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build vector query settings."""
        workspace_ctx = WorkspaceContext(id=workspace_id)
        vector_config = self.get_config_model(workspace_id)

        base_settings = {
            "rag_type": "vector",
            "embedder_type": get_default_embedding_algorithm(),
            "embedder_config": {"base_url": config.llm.ollama_base_url},
            "vector_store_type": "qdrant",
            "vector_store_config": {
                "host": config.vector_store.qdrant_host,
                "port": config.vector_store.qdrant_port,
                "collection_name": workspace_ctx.collection_name,
            },
            "enable_reranking": False,
            "top_k": 5,
        }

        if vector_config:
            base_settings.update(
                {
                    "embedder_type": vector_config.embedding_algorithm,
                    "enable_reranking": vector_config.rerank_algorithm != "none",
                    "reranker_type": vector_config.rerank_algorithm,
                    "top_k": vector_config.top_k,
                }
            )

        return base_settings

    def build_indexing_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build vector indexing settings."""
        workspace_ctx = WorkspaceContext(id=workspace_id)
        vector_config = self.get_config_model(workspace_id)

        base_settings = {
            "rag_type": "vector",
            "parser_type": "text",
            "chunker_type": get_default_chunking_algorithm(),
            "chunker_config": {
                "chunk_size": 500,
                "overlap": 50,
            },
            "embedder_type": get_default_embedding_algorithm(),
            "embedder_config": {
                "base_url": config.llm.ollama_base_url,
            },
            "vector_store_type": "qdrant",
            "vector_store_config": {
                "host": config.vector_store.qdrant_host,
                "port": config.vector_store.qdrant_port,
                "collection_name": workspace_ctx.collection_name,
            },
            "enable_reranking": False,
            "reranker_type": get_default_reranking_algorithm(),
        }

        if vector_config:
            base_settings.update(
                {
                    "chunker_type": vector_config.chunking_algorithm,
                    "chunker_config": {
                        "chunk_size": vector_config.chunk_size,
                        "overlap": vector_config.chunk_overlap,
                    },
                    "embedder_type": vector_config.embedding_algorithm,
                    "enable_reranking": vector_config.rerank_algorithm != "none",
                    "reranker_type": vector_config.rerank_algorithm,
                }
            )

        return base_settings

    def build_provisioning_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build vector provisioning settings."""
        vector_config = self.get_config_model(workspace_id)

        # Get default vector config for provisioning
        base_settings = {
            "rag_type": "vector",
            "qdrant_url": f"http://{config.vector_store.qdrant_host}:{config.vector_store.qdrant_port}",
            "vector_size": 384,  # Default embedding size
            "distance": "cosine",
        }

        if vector_config:
            base_settings.update(
                {
                    "vector_size": vector_config.embedding_model_vector_size,
                    "distance": vector_config.distance_metric,
                }
            )

        return base_settings


class GraphRagConfigProvider(RagConfigProvider):
    """Provider for Graph RAG configuration."""

    def __init__(self, workspace_data_access: WorkspaceDataAccess):
        """Initialize graph RAG config provider.

        Args:
            workspace_data_access: Workspace data access layer
        """
        self.workspace_data_access = workspace_data_access

    def get_config_model(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config model."""
        return self.workspace_data_access.get_graph_rag_config(workspace_id)

    def build_query_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build graph query settings."""
        workspace_ctx = WorkspaceContext(id=workspace_id)
        graph_config = self.get_config_model(workspace_id)

        base_settings = {
            "rag_type": "graph",
            "graph_store_type": "neo4j",
            "graph_store_config": {
                "uri": config.graph_store.neo4j_url,
                "username": config.graph_store.neo4j_user,
                "password": config.graph_store.neo4j_password,
                "database": workspace_ctx.collection_name,
            },
            "max_traversal_depth": 2,
            "top_k_entities": 10,
            "top_k_communities": 3,
            "include_entity_neighborhoods": True,
            "entity_extraction_algorithm": get_default_entity_extraction_algorithm(),
            "relationship_extraction_algorithm": get_default_relationship_extraction_algorithm(),
            "clustering_algorithm": get_default_clustering_algorithm(),
        }

        if graph_config:
            base_settings.update(
                {
                    "entity_extraction_algorithm": graph_config.entity_extraction_algorithm,
                    "relationship_extraction_algorithm": graph_config.relationship_extraction_algorithm,
                    "clustering_algorithm": graph_config.clustering_algorithm,
                    "entity_types": graph_config.entity_types,
                    "relationship_types": graph_config.relationship_types,
                    "max_traversal_depth": graph_config.max_traversal_depth,
                    "top_k_entities": graph_config.top_k_entities,
                    "top_k_communities": graph_config.top_k_communities,
                    "include_entity_neighborhoods": graph_config.include_entity_neighborhoods,
                }
            )

        return base_settings

    def build_indexing_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build graph indexing settings."""
        workspace_ctx = WorkspaceContext(id=workspace_id)
        graph_config = self.get_config_model(workspace_id)

        base_settings = {
            "rag_type": "graph",
            "parser_type": "text",
            "chunker_type": get_default_chunking_algorithm(),
            "chunker_config": {
                "chunk_size": 500,
                "overlap": 50,
            },
            "graph_store_type": "neo4j",
            "graph_store_config": {
                "uri": config.graph_store.neo4j_url,
                "username": config.graph_store.neo4j_user,
                "password": config.graph_store.neo4j_password,
                "database": workspace_ctx.collection_name,
            },
            "entity_extraction_type": get_default_entity_extraction_algorithm(),
            "entity_extraction_config": {
                "entity_types": ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "CONCEPT"],
            },
            "relationship_extraction_type": get_default_relationship_extraction_algorithm(),
            "relationship_extraction_config": {
                "relationship_types": [
                    "WORKS_AT",
                    "LOCATED_IN",
                    "RELATED_TO",
                    "PART_OF",
                    "CREATED_BY",
                ],
            },
            "clustering_algorithm": get_default_clustering_algorithm(),
            "clustering_resolution": 1.0,
            "clustering_max_level": 3,
            "community_min_size": 3,
        }

        if graph_config:
            base_settings.update(
                {
                    "entity_extraction_type": graph_config.entity_extraction_algorithm,
                    "entity_extraction_config": {
                        "entity_types": graph_config.entity_types,
                    },
                    "relationship_extraction_type": graph_config.relationship_extraction_algorithm,
                    "relationship_extraction_config": {
                        "relationship_types": graph_config.relationship_types,
                    },
                    "clustering_algorithm": graph_config.clustering_algorithm,
                    "clustering_resolution": graph_config.clustering_resolution,
                    "clustering_max_level": graph_config.clustering_max_level,
                    "community_min_size": graph_config.community_min_size,
                }
            )

        return base_settings

    def build_provisioning_settings(self, workspace_id: int) -> dict[str, Any]:
        """Build graph provisioning settings."""
        return {
            "rag_type": "graph",
            "graph_store_type": "neo4j",
            "graph_store_config": {
                "uri": config.graph_store.neo4j_url,
                "username": config.graph_store.neo4j_user,
                "password": config.graph_store.neo4j_password,
            },
        }


class RagConfigProviderFactory:
    """Factory for creating RAG config providers.

    This factory eliminates all conditional RAG type checks in service layers
    by providing the appropriate provider based on RAG type.
    """

    def __init__(
        self,
        vector_provider: VectorRagConfigProvider,
        graph_provider: GraphRagConfigProvider,
    ):
        """Initialize factory with providers.

        Args:
            vector_provider: Vector RAG config provider
            graph_provider: Graph RAG config provider
        """
        self._providers = {
            "vector": vector_provider,
            "graph": graph_provider,
        }

    def get_provider(self, rag_type: str) -> Optional[RagConfigProvider]:
        """Get config provider for RAG type.

        Args:
            rag_type: Either "vector" or "graph"

        Returns:
            Appropriate config provider or None if unknown RAG type
        """
        return self._providers.get(rag_type)
