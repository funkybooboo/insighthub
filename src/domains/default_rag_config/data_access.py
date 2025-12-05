"""Default RAG config data access layer - coordinates cache and repository."""

import json
from datetime import datetime
from typing import Optional

from src.domains.default_rag_config.models import (
    DefaultGraphRagConfig,
    DefaultRagConfig,
    DefaultVectorRagConfig,
)
from src.domains.default_rag_config.repositories import DefaultRagConfigRepository
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class DefaultRagConfigDataAccess:
    """Data access layer for DefaultRagConfig - handles caching + persistence."""

    def __init__(self, repository: DefaultRagConfigRepository, cache: Optional[Cache] = None):
        """Initialize data access layer.

        Args:
            repository: DefaultRagConfig repository for database operations
            cache: Optional cache for performance optimization
        """
        self.repository = repository  # Exposed for operations not handled by this layer
        self.cache = cache

    def get(self) -> Optional[DefaultRagConfig]:
        """Get the default RAG config with caching.

        Returns:
            DefaultRagConfig if found, None otherwise
        """
        # Try cache first
        cache_key = "default_rag_config:1"
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
                vector_config = DefaultVectorRagConfig(
                    embedding_algorithm=data["vector_config"]["embedding_algorithm"],
                    chunking_algorithm=data["vector_config"]["chunking_algorithm"],
                    rerank_algorithm=data["vector_config"]["rerank_algorithm"],
                    chunk_size=data["vector_config"]["chunk_size"],
                    chunk_overlap=data["vector_config"]["chunk_overlap"],
                    top_k=data["vector_config"]["top_k"],
                )

                graph_config = DefaultGraphRagConfig(
                    entity_extraction_algorithm=data["graph_config"]["entity_extraction_algorithm"],
                    relationship_extraction_algorithm=data["graph_config"]["relationship_extraction_algorithm"],
                    clustering_algorithm=data["graph_config"]["clustering_algorithm"],
                )

                return DefaultRagConfig(
                    id=data["id"],
                    rag_type=data["rag_type"],
                    vector_config=vector_config,
                    graph_config=graph_config,
                    created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
                    updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
                )
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                logger.warning(f"Cache deserialization error for default RAG config: {e}")

        # Cache miss - fetch from database
        config = self.repository.get()

        if config and self.cache:
            self._cache_config(config)

        return config

    def update(self, config: DefaultRagConfig) -> DefaultRagConfig:
        """Update the default RAG config.

        Args:
            config: DefaultRagConfig to update

        Returns:
            Updated config
        """
        updated_config = self.repository.update(config)
        self._invalidate_cache()
        return updated_config

    def _cache_config(self, config: DefaultRagConfig) -> None:
        """Cache config data.

        Args:
            config: DefaultRagConfig to cache
        """
        if not self.cache:
            return

        cache_key = "default_rag_config:1"
        cache_value = json.dumps({
            "id": config.id,
            "rag_type": config.rag_type,
            "vector_config": {
                "embedding_algorithm": config.vector_config.embedding_algorithm,
                "chunking_algorithm": config.vector_config.chunking_algorithm,
                "rerank_algorithm": config.vector_config.rerank_algorithm,
                "chunk_size": config.vector_config.chunk_size,
                "chunk_overlap": config.vector_config.chunk_overlap,
                "top_k": config.vector_config.top_k,
            },
            "graph_config": {
                "entity_extraction_algorithm": config.graph_config.entity_extraction_algorithm,
                "relationship_extraction_algorithm": config.graph_config.relationship_extraction_algorithm,
                "clustering_algorithm": config.graph_config.clustering_algorithm,
            },
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        })
        self.cache.set(cache_key, cache_value, ttl=600)  # Cache for 10 minutes (config changes rarely)

    def _invalidate_cache(self) -> None:
        """Invalidate config cache."""
        if self.cache:
            cache_key = "default_rag_config:1"
            self.cache.delete(cache_key)
