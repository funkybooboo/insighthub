"""Pytest configuration and shared fixtures."""

# IMPORTANT: Load test environment configuration BEFORE importing any src modules
# This must be at the very top to ensure config values are loaded before src.config is imported
from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

# Now safe to import src modules which will use the test configuration
import os
from collections.abc import Generator
from io import BytesIO
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest
from flask import Flask
from flask.testing import FlaskClient
from shared.database.sql import PostgresSqlDatabase
from shared.models import User
from shared.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    UserRepository,
)
from shared.storage import BlobStorage
from shared.storage.s3_blob_storage import S3BlobStorage
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer

from src import config
from src.api import create_app
from tests.context import IntegrationTestContext, create_integration_test_context


def _run_migrations(db_url: str) -> None:
    """Run migration SQL files against the database."""
    migrations_dir = Path(__file__).parent.parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            for migration_file in migration_files:
                sql = migration_file.read_text()
                cur.execute(sql)
        conn.commit()
    finally:
        conn.close()


def _drop_all_tables(db_url: str) -> None:
    """Drop all tables from the database."""
    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        conn.commit()
    finally:
        conn.close()


# ============================================================================
# Pytest Skip Helpers
# ============================================================================


def skip_if_no_openai() -> pytest.MarkDecorator:
    """Skip test if OpenAI API key is not configured."""
    return pytest.mark.skipif(
        not config.OPENAI_API_KEY,
        reason="OpenAI API key not configured (set OPENAI_API_KEY in .env)",
    )


def skip_if_no_ollama() -> pytest.MarkDecorator:
    """Skip test if Ollama is not running."""
    import requests

    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=2)
        ollama_available = response.status_code == 200
    except Exception:
        ollama_available = False

    return pytest.mark.skipif(
        not ollama_available,
        reason=f"Ollama not available at {config.OLLAMA_BASE_URL}",
    )


def skip_if_no_qdrant() -> pytest.MarkDecorator:
    """Skip test if Qdrant is not running."""
    import requests

    try:
        response = requests.get(
            f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}/healthz", timeout=2
        )
        qdrant_available = response.status_code == 200
    except Exception:
        qdrant_available = False

    return pytest.mark.skipif(
        not qdrant_available,
        reason=f"Qdrant not available at {config.QDRANT_HOST}:{config.QDRANT_PORT}",
    )


# ============================================================================
# Integration Test Fixtures (Testcontainers)
# ============================================================================


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
        config_dict = minio.get_config()
        print(f"[TESTCONTAINERS] MinIO started: {config_dict['endpoint']}")
        yield minio
        print("[TESTCONTAINERS] Stopping MinIO container...")


@pytest.fixture(scope="function")
def db_url(postgres_container: PostgresContainer) -> Generator[str, None, None]:
    """Get database URL and run migrations."""
    url = postgres_container.get_connection_url()

    # Run migrations
    _run_migrations(url)

    yield url

    # Drop all tables after test
    _drop_all_tables(url)


@pytest.fixture(scope="function")
def db(db_url: str) -> Generator[PostgresSqlDatabase, None, None]:
    """Create a test database connection."""
    database = PostgresSqlDatabase(db_url)
    try:
        yield database
    finally:
        database.close()


@pytest.fixture(scope="function")
def test_database_url(postgres_container: PostgresContainer) -> str:
    """Get the database URL for testing."""
    url: str = postgres_container.get_connection_url()
    return url


@pytest.fixture(scope="function")
def app(postgres_container: PostgresContainer, blob_storage: BlobStorage) -> Flask:
    """Create Flask app for testing with test database."""
    # Set up database URL from testcontainer
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url()

    # Create app (BLOB_STORAGE_TYPE already set at module level)
    test_app = create_app()
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def blob_storage(minio_container: MinioContainer) -> BlobStorage:
    """Create a test blob storage instance with MinIO container."""
    minio_config = minio_container.get_config()
    endpoint = minio_config["endpoint"]

    # Ensure endpoint has protocol
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"http://{endpoint}"

    return S3BlobStorage(
        endpoint=endpoint,
        access_key=minio_config["access_key"],
        secret_key=minio_config["secret_key"],
        bucket_name="test-bucket",
        secure=False,
    )


@pytest.fixture(scope="function")
def test_context(db: PostgresSqlDatabase, blob_storage: BlobStorage) -> IntegrationTestContext:
    """Create a test context for integration tests with real implementations."""
    return create_integration_test_context(db=db, blob_storage=blob_storage)


@pytest.fixture(scope="function")
def user_repository(test_context: IntegrationTestContext) -> UserRepository:
    """Get user repository from test context."""
    return test_context.user_repository


@pytest.fixture(scope="function")
def document_repository(test_context: IntegrationTestContext) -> DocumentRepository:
    """Get document repository from test context."""
    return test_context.document_repository


@pytest.fixture(scope="function")
def chat_session_repository(test_context: IntegrationTestContext) -> ChatSessionRepository:
    """Get chat session repository from test context."""
    return test_context.chat_session_repository


@pytest.fixture(scope="function")
def chat_message_repository(test_context: IntegrationTestContext) -> ChatMessageRepository:
    """Get chat message repository from test context."""
    return test_context.chat_message_repository


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_text_file() -> BytesIO:
    """Create a sample text file for testing."""
    content = b"This is a test document.\nIt has multiple lines.\nFor testing purposes."
    return BytesIO(content)


@pytest.fixture
def test_user(db: PostgresSqlDatabase) -> User:
    """Create a test user for authentication."""
    password_hash = User.hash_password("test_password")

    row = db.fetchone(
        """
        INSERT INTO users (username, email, password_hash, full_name)
        VALUES (%(username)s, %(email)s, %(password_hash)s, %(full_name)s)
        RETURNING *
        """,
        {
            "username": "test_user",
            "email": "test@example.com",
            "password_hash": password_hash,
            "full_name": "Test User",
        },
    )
    assert row is not None

    return User(**row)


@pytest.fixture
def test_token(test_user: User) -> str:
    """Create a JWT token for the test user."""
    from src.infrastructure.auth import create_access_token

    return create_access_token(test_user.id)


@pytest.fixture
def auth_headers(test_token: str) -> dict[str, str]:
    """Create authentication headers with Bearer token."""
    return {"Authorization": f"Bearer {test_token}"}


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
