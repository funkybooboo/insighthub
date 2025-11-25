import io
import os
import uuid

import psycopg2  # type: ignore
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer


def test_parser_worker_database_operations_integration(
    postgres_container: PostgresContainer,
    minio_container: MinioContainer,
) -> None:
    """Test ParserWorker database operations and basic connectivity."""
    # Set environment variables BEFORE importing ParserWorker
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    os.environ["DATABASE_URL"] = db_url
    os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/%2F"
    minio_host_port = f"{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}"
    os.environ["S3_ENDPOINT_URL"] = minio_host_port
    os.environ["S3_ACCESS_KEY"] = "minioadmin"
    os.environ["S3_SECRET_KEY"] = "minioadmin"
    os.environ["S3_BUCKET_NAME"] = "test-bucket"

    # Now import ParserWorker after environment is set
    from src.main import ParserWorker  # noqa: E402

    # Test that worker can be created (validates database connection)
    worker = ParserWorker()

    # Test that database connection works by checking if we can get a cursor
    with worker.db_connection.get_cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result == (1,)

    # Test document status updates
    document_id = str(uuid.uuid4())

    # Create test table
    with worker.db_connection.get_cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                processing_status TEXT,
                processing_metadata JSONB,
                parsed_text TEXT,
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """
        )
        cursor.execute(
            """
            INSERT INTO documents (id, processing_status)
            VALUES (%s, %s)
        """,
            (document_id, "uploaded"),
        )
    worker.db_connection.commit()

    # Test status updates
    worker._update_document_status(document_id, "parsing")
    worker._update_document_status(document_id, "parsed", {"text_length": 100})

    # Verify status was updated
    with worker.db_connection.get_cursor() as cursor:
        cursor.execute(
            "SELECT processing_status, processing_metadata FROM documents WHERE id = %s",
            (document_id,),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "parsed"
        assert row[1]["text_length"] == 100

    # Test parsed text storage
    test_text = "This is parsed text content."
    worker._store_parsed_text(document_id, test_text)

    # Verify text was stored
    with worker.db_connection.get_cursor() as cursor:
        cursor.execute(
            "SELECT parsed_text FROM documents WHERE id = %s", (document_id,)
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == test_text

    worker.db_connection.close()


def test_document_parser_with_minio_integration(
    postgres_container: PostgresContainer,
    minio_container: MinioContainer,
) -> None:
    """Test document parsing with MinIO storage integration."""
    # Set environment variables
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    os.environ["DATABASE_URL"] = db_url
    minio_host_port = f"{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}"
    os.environ["S3_ENDPOINT_URL"] = f"http://{minio_host_port}"
    os.environ["S3_ACCESS_KEY"] = "minioadmin"
    os.environ["S3_SECRET_KEY"] = "minioadmin"
    os.environ["S3_BUCKET_NAME"] = "test-bucket"

    from src.main import DocumentParser  # noqa: E402

    # Create test document content
    test_content = (
        "This is a test document.\nIt has multiple lines.\nAnd special chars: àáâãäå."
    )

    # Set up blob storage
    from shared.storage.s3_blob_storage import S3BlobStorage  # noqa: E402

    blob_storage = S3BlobStorage(
        endpoint=f"http://{minio_host_port}",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket_name="test-bucket",
        secure=False,
    )

    # Upload test document
    document_id = str(uuid.uuid4())
    file_path = f"documents/{document_id}/test.txt"
    file_obj = io.BytesIO(test_content.encode("utf-8"))
    upload_result = blob_storage.upload_file(file_obj, file_path)
    assert (
        upload_result.is_ok()
    ), f"Failed to upload test document: {upload_result.err()}"

    # Create document parser and test parsing
    parser = DocumentParser()
    parsed_text = parser.parse_document(document_id, "text/plain", file_path)

    # Verify the content was parsed correctly
    assert parsed_text == test_content


def test_document_parser_error_handling_integration(
    postgres_container: PostgresContainer,
    minio_container: MinioContainer,
) -> None:
    """Test document parser error handling for invalid files."""
    # Set environment variables
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )
    os.environ["DATABASE_URL"] = db_url
    minio_host_port = f"{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}"
    os.environ["S3_ENDPOINT_URL"] = f"http://{minio_host_port}"
    os.environ["S3_ACCESS_KEY"] = "minioadmin"
    os.environ["S3_SECRET_KEY"] = "minioadmin"
    os.environ["S3_BUCKET_NAME"] = "test-bucket"

    from src.main import DocumentParser  # noqa: E402

    # Create document parser
    parser = DocumentParser()

    # Test parsing non-existent file
    document_id = str(uuid.uuid4())
    invalid_file_path = f"documents/{document_id}/nonexistent.pdf"

    # Should raise an exception for non-existent file
    try:
        parser.parse_document(document_id, "application/pdf", invalid_file_path)
        assert False, "Expected exception for non-existent file"
    except Exception as e:
        # Expected to fail with download error
        assert "DOWNLOAD_ERROR" in str(e) or "No parser available" in str(e)


def test_postgres_connection_integration(postgres_container: PostgresContainer) -> None:
    """Test PostgreSQL connection and basic operations."""
    db_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql://"
    )

    # Test connection
    conn = psycopg2.connect(db_url)
    assert conn is not None

    # Test basic operations
    with conn.cursor() as cursor:
        cursor.execute("CREATE TABLE test_table (id SERIAL PRIMARY KEY, data TEXT)")
        cursor.execute("INSERT INTO test_table (data) VALUES (%s)", ("test data",))
        cursor.execute("SELECT data FROM test_table WHERE id = 1")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "test data"

    conn.close()


def test_minio_storage_integration(minio_container: MinioContainer) -> None:
    """Test MinIO storage operations."""
    minio_host_port = f"{minio_container.get_container_host_ip()}:{minio_container.get_exposed_port(9000)}"

    from shared.storage.s3_blob_storage import S3BlobStorage  # noqa: E402

    # Create storage client
    storage = S3BlobStorage(
        endpoint=f"http://{minio_host_port}",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket_name="test-bucket",
        secure=False,
    )

    # Test file upload
    test_content = b"Hello, MinIO!"
    file_obj = io.BytesIO(test_content)
    object_name = "test-file.txt"

    upload_result = storage.upload_file(file_obj, object_name)
    assert upload_result.is_ok()

    # Test file download
    download_result = storage.download_file(object_name)
    assert download_result.is_ok()
    assert download_result.unwrap() == test_content

    # Test file existence
    assert storage.file_exists(object_name) is True
    assert storage.file_exists("nonexistent.txt") is False

    # Test file deletion
    delete_result = storage.delete_file(object_name)
    assert delete_result.is_ok()
    assert storage.file_exists(object_name) is False
