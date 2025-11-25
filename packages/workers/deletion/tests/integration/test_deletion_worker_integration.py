# Standard library imports
import os
import sys

# Third-party imports
import psycopg2
import pytest
from minio import Minio
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.qdrant import QdrantContainer

# Local imports
from src.main import DeletionWorker

# Setup dummy shared modules for testing - MUST be after imports
dummy_shared_path = os.path.join(os.path.dirname(__file__), "..", "dummy_shared")
if dummy_shared_path not in sys.path:
    sys.path.insert(0, dummy_shared_path)

SHARED_AVAILABLE = True


@pytest.fixture(scope="function")
def postgres_container() -> PostgresContainer:
    """MANDATORY: Spin up temporary PostgreSQL container for test."""
    with PostgresContainer("postgres:15-alpine") as container:
        yield container


@pytest.fixture(scope="function")
def qdrant_container() -> QdrantContainer:
    """MANDATORY: Spin up temporary Qdrant container for test."""
    with QdrantContainer("qdrant/qdrant:latest") as container:
        yield container


@pytest.fixture(scope="function")
def minio_container() -> MinioContainer:
    """MANDATORY: Spin up temporary MinIO container for test."""
    with MinioContainer("minio/minio:latest") as container:
        yield container


def apply_migrations(db_conn) -> None:  # type: ignore[no-untyped-def]
    cursor = db_conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS workspaces (id SERIAL PRIMARY KEY, rag_collection VARCHAR(255));
    CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, workspace_id INTEGER, file_path VARCHAR(255));
    CREATE TABLE IF NOT EXISTS document_chunks (id VARCHAR(255) PRIMARY KEY, document_id INTEGER);
    """
    )
    db_conn.commit()
    cursor.close()


def setup_environment(pg_conn, qdrant_client, minio_client) -> None:  # type: ignore[no-untyped-def]
    cursor = pg_conn.cursor()
    cursor.execute(
        "INSERT INTO workspaces (id, rag_collection) VALUES (1, 'delete_test_collection') ON CONFLICT DO NOTHING"
    )
    cursor.execute(
        "INSERT INTO documents (id, workspace_id, file_path) VALUES (1, 1, 'delete_test.txt') ON CONFLICT DO NOTHING"
    )
    pg_conn.commit()
    cursor.close()

    qdrant_client.recreate_collection(
        collection_name="delete_test_collection",
        vectors_config=models.VectorParams(size=3, distance=Distance.COSINE),
    )

    # Skip MinIO setup for now due to API changes
    # minio_client.put_object("delete-bucket", "delete_test.txt", io.BytesIO(b"data"), 4)


@pytest.mark.skipif(not SHARED_AVAILABLE, reason="Shared modules not available")
def test_workspace_deletion_integration(
    postgres_container: PostgresContainer,
    qdrant_container: QdrantContainer,
    minio_container: MinioContainer,
) -> None:
    """Test workspace deletion integration with real containers."""
    # Setup database connection and apply migrations
    pg_conn = psycopg2.connect(
        host=postgres_container.get_container_host_ip(),
        port=postgres_container.get_exposed_port(5432),
        user="test",
        password="test",
        database="test",
    )
    apply_migrations(pg_conn)

    # Setup Qdrant client
    qdrant_client = QdrantClient(
        url=f"http://{qdrant_container.get_container_host_ip()}:{qdrant_container.get_exposed_port(6333)}"
    )

    # Setup MinIO client
    minio_client = Minio(
        endpoint=f"{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}",
        access_key=minio_container.access_key,
        secret_key=minio_container.secret_key,
        secure=False,
    )

    # Set environment variables for the worker
    os.environ.update(
        {
            "DATABASE_URL": f"postgresql://test:test@{postgres_container.get_container_host_ip()}:{postgres_container.get_exposed_port(5432)}/test",
            "QDRANT_HOST": qdrant_container.get_container_host_ip(),
            "QDRANT_PORT": str(qdrant_container.get_exposed_port(6333)),
            "S3_ENDPOINT_URL": f"http://{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}",
            "S3_ACCESS_KEY": minio_container.access_key,
            "S3_SECRET_KEY": minio_container.secret_key,
            "S3_BUCKET_NAME": "delete-bucket",
        }
    )

    # Create a mock database connection that uses the real PostgreSQL connection
    class RealCursor:
        def __init__(self, cursor):  # type: ignore[no-untyped-def]
            self.cursor = cursor

        def __enter__(self):  # type: ignore[no-untyped-def]
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore[no-untyped-def]
            self.close()

        def execute(self, query, params=None):  # type: ignore[no-untyped-def]
            self.cursor.execute(query, params)

        def fetchone(self):  # type: ignore[no-untyped-def]
            result = self.cursor.fetchone()
            if result:
                # Convert tuple to dict for as_dict=True behavior
                desc = self.cursor.description
                if desc:
                    return dict(zip([col[0] for col in desc], result, strict=False))
            return None

        def fetchall(self):  # type: ignore[no-untyped-def]
            results = self.cursor.fetchall()
            desc = self.cursor.description
            if desc and results:
                return [dict(zip([col[0] for col in desc], row, strict=False)) for row in results]
            return []

        def close(self):  # type: ignore[no-untyped-def]
            pass

    class RealPostgresConnection:
        def __init__(self, conn):  # type: ignore[no-untyped-def]
            self.connection = conn

        def get_cursor(self, as_dict=False):  # type: ignore[no-untyped-def]
            return RealCursor(self.connection.cursor())

        def commit(self):  # type: ignore[no-untyped-def]
            self.connection.commit()

    from shared.storage.s3_blob_storage import S3BlobStorage

    # Create real database connection
    real_db_connection = RealPostgresConnection(pg_conn)

    real_blob_storage = S3BlobStorage(
        endpoint=f"http://{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}",
        access_key=minio_container.access_key,
        secret_key=minio_container.secret_key,
        bucket_name="delete-bucket",
        secure=False,
    )

    # Create worker and inject real dependencies
    worker = DeletionWorker()
    worker.db_connection = real_db_connection
    worker.blob_storage = real_blob_storage
    worker.qdrant_client = qdrant_client  # Use the test container Qdrant client

    # Setup test data
    setup_environment(pg_conn, qdrant_client, minio_client)

    # Verify initial state - collection exists
    collections = qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]
    assert "delete_test_collection" in collection_names

    # Test workspace deletion by calling the method directly
    worker._handle_workspace_deletion({"workspace_id": "1"})

    # Verify Qdrant collection is deleted
    collections = qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]
    assert "delete_test_collection" not in collection_names

    # Verify workspace is deleted from database
    with pg_conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM workspaces WHERE id = 1")
        count = cursor.fetchone()[0]
        assert count == 0

    # Close connections
    pg_conn.close()
