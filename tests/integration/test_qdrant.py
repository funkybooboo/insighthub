"""Integration test for Qdrant using testcontainers.

Tests basic Qdrant functionality with a real database instance.
"""

import pytest
from testcontainers.core.container import DockerContainer


@pytest.mark.integration
class TestQdrantIntegration:
    """Qdrant integration tests using testcontainers."""

    @pytest.fixture(scope="function")
    def qdrant_container(self):
        """Spin up a Qdrant container for testing."""
        container = DockerContainer("qdrant/qdrant:latest").with_exposed_ports(6333)
        container.start()
        yield container
        container.stop()

    def test_qdrant_container_starts(self, qdrant_container):
        """Test that Qdrant container starts successfully."""
        # Get connection details
        host = qdrant_container.get_container_host_ip()
        port = qdrant_container.get_exposed_port(6333)

        # Assert we can get host and port
        assert host is not None
        assert port is not None
        assert int(port) > 0
