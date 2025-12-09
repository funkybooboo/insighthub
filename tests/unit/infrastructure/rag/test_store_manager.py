"""Unit tests for the RAGStoreManager."""

import unittest
from unittest.mock import MagicMock, patch

from src.infrastructure.store_manager import RAGStoreManager


class TestRAGStoreManager(unittest.TestCase):
    """Unit tests for the RAGStoreManager."""

    def setUp(self):
        """Set up the test case."""
        self.manager = RAGStoreManager()

    @patch("src.infrastructure.vector_stores.VectorStoreFactory.create_vector_store")
    def test_get_vector_store_caches_by_config(self, mock_create):
        """Test that get_vector_store caches stores per configuration."""
        mock_store1 = MagicMock()
        mock_store2 = MagicMock()
        mock_create.side_effect = [mock_store1, mock_store2]

        rag_config1 = {
            "vector_store_type": "qdrant",
            "vector_store_config": {
                "host": "localhost",
                "port": 6333,
                "collection_name": "workspace_1",
            },
        }

        # First call should create the store
        store1 = self.manager.get_vector_store(rag_config1)
        self.assertIs(store1, mock_store1)
        mock_create.assert_called_once_with(
            "qdrant", host="localhost", port=6333, collection_name="workspace_1"
        )

        # Second call with same config should return cached instance
        mock_create.reset_mock()
        store1_again = self.manager.get_vector_store(rag_config1)
        self.assertIs(store1_again, mock_store1)
        mock_create.assert_not_called()

        # Third call with different collection should create new instance
        rag_config2 = {
            "vector_store_type": "qdrant",
            "vector_store_config": {
                "host": "localhost",
                "port": 6333,
                "collection_name": "workspace_2",
            },
        }
        store2 = self.manager.get_vector_store(rag_config2)
        self.assertIs(store2, mock_store2)
        self.assertIsNot(store2, mock_store1)
        mock_create.assert_called_once_with(
            "qdrant", host="localhost", port=6333, collection_name="workspace_2"
        )

    @patch("src.infrastructure.graph_stores.factory.GraphStoreFactory.create")
    def test_get_graph_store_caches_by_config(self, mock_create):
        """Test that get_graph_store caches stores per configuration."""
        mock_store1 = MagicMock()
        mock_store2 = MagicMock()
        mock_create.side_effect = [mock_store1, mock_store2]

        rag_config1 = {
            "graph_store_type": "neo4j",
            "graph_store_config": {"uri": "bolt://localhost:7687", "database": "workspace_1"},
        }

        # First call should create the store
        store1 = self.manager.get_graph_store(rag_config1)
        self.assertIs(store1, mock_store1)
        mock_create.assert_called_once_with(
            "neo4j", uri="bolt://localhost:7687", database="workspace_1"
        )

        # Second call with same config should return cached instance
        mock_create.reset_mock()
        store1_again = self.manager.get_graph_store(rag_config1)
        self.assertIs(store1_again, mock_store1)
        mock_create.assert_not_called()

        # Third call with different database should create new instance
        rag_config2 = {
            "graph_store_type": "neo4j",
            "graph_store_config": {"uri": "bolt://localhost:7687", "database": "workspace_2"},
        }
        store2 = self.manager.get_graph_store(rag_config2)
        self.assertIs(store2, mock_store2)
        self.assertIsNot(store2, mock_store1)
        mock_create.assert_called_once_with(
            "neo4j", uri="bolt://localhost:7687", database="workspace_2"
        )

    @patch("src.infrastructure.vector_stores.VectorStoreFactory.create_vector_store")
    def test_vector_cache_key_generation(self, mock_create):
        """Test that vector cache keys are generated correctly."""
        mock_store = MagicMock()
        mock_create.return_value = mock_store

        config = {
            "vector_store_type": "qdrant",
            "vector_store_config": {"collection_name": "test_collection"},
        }

        key = self.manager._make_vector_cache_key(config)
        self.assertEqual(key, "qdrant:test_collection")

    @patch("src.infrastructure.graph_stores.factory.GraphStoreFactory.create")
    def test_graph_cache_key_generation(self, mock_create):
        """Test that graph cache keys are generated correctly."""
        mock_store = MagicMock()
        mock_create.return_value = mock_store

        config = {
            "graph_store_type": "neo4j",
            "graph_store_config": {"database": "test_db"},
        }

        key = self.manager._make_graph_cache_key(config)
        self.assertEqual(key, "neo4j:test_db")


if __name__ == "__main__":
    unittest.main()
