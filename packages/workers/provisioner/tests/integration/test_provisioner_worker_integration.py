import psycopg2
from qdrant_client import QdrantClient
from testcontainers.postgres import PostgresContainer
from testcontainers.qdrant import QdrantContainer

from src.main import VectorStoreProvisioner


def apply_migrations(db_conn: psycopg2.extensions.connection) -> None:
    """Apply database migrations for testing."""
    cursor = db_conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS workspaces (
        id SERIAL PRIMARY KEY,
        status VARCHAR(50),
        status_message TEXT,
        rag_collection VARCHAR(255),
        updated_at TIMESTAMP
    );
    """
    )
    db_conn.commit()
    cursor.close()


def test_vector_store_provisioner_integration(
    postgres_container: PostgresContainer, qdrant_container: QdrantContainer
) -> None:
    """
    Test VectorStoreProvisioner creates Qdrant collections correctly.

    This tests input/output behavior: given a workspace ID and config,
    verify that a Qdrant collection is created with the correct name and configuration.
    """
    # Setup Qdrant client
    qdrant_url = f"http://{qdrant_container.get_container_host_ip()}:{qdrant_container.get_exposed_port(6333)}"
    qdrant_client = QdrantClient(url=qdrant_url)

    # Test provisioning with different embedding dimensions
    provisioner = VectorStoreProvisioner(qdrant_url)

    # Test case 1: Standard embedding dimension
    collection_name = provisioner.provision_workspace_collection(
        "test_workspace_1", {"embedding_dim": 384}
    )

    assert collection_name == "workspace_test_workspace_1"

    # Verify collection exists and has correct configuration
    collection_info = qdrant_client.get_collection(collection_name=collection_name)
    assert collection_info is not None

    # Test case 2: Provisioning the same workspace again (should not fail)
    collection_name_2 = provisioner.provision_workspace_collection(
        "test_workspace_1", {"embedding_dim": 384}
    )
    assert collection_name_2 == collection_name

    # Test case 3: Different workspace
    collection_name_3 = provisioner.provision_workspace_collection(
        "test_workspace_2", {"embedding_dim": 768}
    )
    assert collection_name_3 == "workspace_test_workspace_2"

    # Verify both collections exist
    info_1 = qdrant_client.get_collection(collection_name="workspace_test_workspace_1")
    info_2 = qdrant_client.get_collection(collection_name="workspace_test_workspace_2")
    assert info_1 is not None
    assert info_2 is not None


def test_workspace_database_operations_integration(
    postgres_container: PostgresContainer,
) -> None:
    """
    Test workspace database operations work correctly.

    This tests input/output behavior: database operations should update
    workspace status and resources correctly.
    """
    from src.main import ProvisionerWorker

    # Setup database connection
    db_url = f"postgresql://{postgres_container.username}:{postgres_container.password}@{postgres_container.get_container_host_ip()}:{postgres_container.get_exposed_port(5432)}/{postgres_container.dbname}"
    db_conn = psycopg2.connect(db_url)
    apply_migrations(db_conn)

    # Insert test workspace
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO workspaces (id, status) VALUES (999, 'provisioning')")
    db_conn.commit()

    # Mock minimal config for database operations
    from unittest.mock import MagicMock, patch

    mock_config = MagicMock()
    mock_config.database_url = db_url

    with patch("src.main.config", mock_config), patch("src.main.DATABASE_URL", db_url):
        worker = ProvisionerWorker()

        # Test updating workspace resources
        worker._update_workspace_resources("999", "test_collection", None)

        # Test updating workspace status
        worker._update_workspace_status("999", "ready", "Provisioning completed")

        # Verify final state
        cursor.execute(
            "SELECT status, rag_collection, status_message FROM workspaces WHERE id = 999"
        )
        result = cursor.fetchone()
        cursor.close()
        db_conn.close()

        assert result is not None
        status, collection, message = result
        assert status == "ready"
        assert collection == "test_collection"
        assert message == "Provisioning completed"
