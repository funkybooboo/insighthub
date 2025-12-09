"""RAG Store Manager."""

import json
from typing import Dict

from src.infrastructure.graph_stores.factory import GraphStoreFactory
from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.vector_stores import VectorStoreFactory
from src.infrastructure.vector_stores.vector_store import VectorStore


class RAGStoreManager:
    """Manages RAG stores with caching based on configuration.

    This manager maintains separate store instances for different configurations
    (e.g., different collections or databases) to support multi-workspace scenarios.
    """

    def __init__(self) -> None:
        """Initialize the RAG store manager."""
        self._vector_stores: Dict[str, VectorStore] = {}
        self._graph_stores: Dict[str, GraphStore] = {}

    def _make_vector_cache_key(self, rag_config: dict) -> str:
        """Create a cache key from vector store configuration.

        Args:
            rag_config: RAG configuration dict

        Returns:
            Cache key string based on store type and config
        """
        vector_store_type = rag_config.get("vector_store_type", "qdrant")
        vector_store_config = rag_config.get("vector_store_config", {})

        # Create deterministic key from config (collection_name is the critical differentiator)
        key_parts = [vector_store_type]

        # For Qdrant, collection_name is the key differentiator
        if "collection_name" in vector_store_config:
            key_parts.append(vector_store_config["collection_name"])
        else:
            # Fallback: serialize entire config for uniqueness
            key_parts.append(json.dumps(vector_store_config, sort_keys=True))

        return ":".join(key_parts)

    def _make_graph_cache_key(self, rag_config: dict) -> str:
        """Create a cache key from graph store configuration.

        Args:
            rag_config: RAG configuration dict

        Returns:
            Cache key string based on store type and config
        """
        graph_store_type = rag_config.get("graph_store_type", "neo4j")
        graph_store_config = rag_config.get("graph_store_config", {})

        # Create deterministic key from config (database is the critical differentiator)
        key_parts = [graph_store_type]

        # For Neo4j, database name is the key differentiator
        if "database" in graph_store_config:
            key_parts.append(graph_store_config["database"])
        else:
            # Fallback: serialize entire config for uniqueness
            key_parts.append(json.dumps(graph_store_config, sort_keys=True))

        return ":".join(key_parts)

    def get_vector_store(self, rag_config: dict) -> VectorStore:
        """Get or create a vector store for the given configuration.

        Args:
            rag_config: RAG configuration containing vector_store_type and vector_store_config

        Returns:
            VectorStore instance (cached if same config used before)
        """
        cache_key = self._make_vector_cache_key(rag_config)

        if cache_key not in self._vector_stores:
            vector_store_type = rag_config.get("vector_store_type", "qdrant")
            vector_store_config = rag_config.get("vector_store_config", {})
            self._vector_stores[cache_key] = VectorStoreFactory.create_vector_store(
                vector_store_type, **vector_store_config
            )

        return self._vector_stores[cache_key]

    def get_graph_store(self, rag_config: dict) -> GraphStore:
        """Get or create a graph store for the given configuration.

        Args:
            rag_config: RAG configuration containing graph_store_type and graph_store_config

        Returns:
            GraphStore instance (cached if same config used before)
        """
        cache_key = self._make_graph_cache_key(rag_config)

        if cache_key not in self._graph_stores:
            graph_store_type = rag_config.get("graph_store_type", "neo4j")
            graph_store_config = rag_config.get("graph_store_config", {})
            self._graph_stores[cache_key] = GraphStoreFactory.create(
                graph_store_type, **graph_store_config
            )

        return self._graph_stores[cache_key]
