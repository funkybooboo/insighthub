"""Integration test for Qdrant using testcontainers.

Tests basic Qdrant functionality with a real database instance.
"""

import pytest
from testcontainers.qdrant import QdrantContainer


@pytest.mark.integration
class TestQdrantIntegration:
    """Qdrant integration tests using testcontainers."""

    @pytest.fixture(scope="function")
    def qdrant_container(self):
        """Spin up a Qdrant container for testing."""
        container = QdrantContainer("qdrant/qdrant:v1.9.1")
        container.start()
        yield container
        container.stop()

    def test_qdrant_container_starts(self, qdrant_container):
        """Test that Qdrant container starts successfully."""
        # Get connection details
        host = qdrant_container.get_container_host_ip()
        port = qdrant_container.exposed_rest_port

        # Assert we can get host and port
        assert host is not None
        assert port is not None
        assert int(port) > 0

    def test_qdrant_client_connection(self, qdrant_container):
        """Test that we can connect to Qdrant and perform basic operations."""
        # Get a client from the container
        client = qdrant_container.get_client()

        # Test basic operation - get collections (should be empty initially)
        collections = client.get_collections()
        assert collections is not None
