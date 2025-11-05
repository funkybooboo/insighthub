"""Pytest configuration and fixtures."""

import os
from io import BytesIO
from typing import Any, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer

from src.db.base import Base
from src.storage.blob_storage import S3BlobStorage


@pytest.fixture(scope="session", autouse=False)
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    Start a PostgreSQL container for the test session.

    This fixture automatically starts a PostgreSQL 16 container when any test
    that depends on it (directly or indirectly) runs. The container is shared
    across all tests in the session for performance.

    The container is automatically stopped and removed after all tests complete.
    """
    print("\n[TESTCONTAINERS] Starting PostgreSQL container...")
    with PostgresContainer("postgres:16-alpine") as postgres:
        print(f"[TESTCONTAINERS] PostgreSQL started: {postgres.get_connection_url()}")
        yield postgres
        print("[TESTCONTAINERS] Stopping PostgreSQL container...")


@pytest.fixture(scope="session", autouse=False)
def minio_container() -> Generator[MinioContainer, None, None]:
    """
    Start a MinIO container for the test session.

    This fixture automatically starts a MinIO (S3-compatible) container when any
    test that depends on it (directly or indirectly) runs. The container is shared
    across all tests in the session for performance.

    The container is automatically stopped and removed after all tests complete.
    """
    print("\n[TESTCONTAINERS] Starting MinIO container...")
    with MinioContainer() as minio:
        config = minio.get_config()
        print(f"[TESTCONTAINERS] MinIO started: {config['endpoint']}")
        yield minio
        print("[TESTCONTAINERS] Stopping MinIO container...")


@pytest.fixture(scope="function")
def db_engine(postgres_container: PostgresContainer) -> Generator[Any, None, None]:
    """Create a test database engine with temporary PostgreSQL container."""
    # Get connection URL from container
    db_url = postgres_container.get_connection_url()

    # Create engine
    engine = create_engine(db_url, pool_pre_ping=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine: Any) -> Generator[Session, None, None]:
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_database_url(postgres_container: PostgresContainer) -> str:
    """Get the database URL for testing."""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="function")
def blob_storage(minio_container: MinioContainer) -> S3BlobStorage:
    """Create a test blob storage instance with MinIO container."""
    minio_config = minio_container.get_config()
    endpoint = minio_config["endpoint"]

    # Ensure endpoint has protocol
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"http://{endpoint}"

    return S3BlobStorage(
        endpoint_url=endpoint,
        access_key=minio_config["access_key"],
        secret_key=minio_config["secret_key"],
        bucket_name="test-bucket",
    )


@pytest.fixture
def sample_text_file() -> BytesIO:
    """Create a sample text file for testing."""
    content = b"This is a test document.\nIt has multiple lines.\nFor testing purposes."
    return BytesIO(content)


@pytest.fixture
def sample_pdf_file() -> BytesIO:
    """Create a sample PDF file for testing."""
    # Minimal valid PDF
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
409
%%EOF"""
    return BytesIO(pdf_content)
