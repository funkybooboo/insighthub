"""Test configuration module.

This module provides clear, centralized configuration for all tests.
It makes it easy to understand what settings are used for different test scenarios.
"""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class TestDatabaseConfig:
    """Configuration for test database connections."""

    __test__ = False  # Tell pytest this is not a test class

    # PostgreSQL container settings (for integration tests)
    POSTGRES_IMAGE: str = "postgres:16-alpine"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    POSTGRES_DB: str = "test_db"

    # SQLite settings (for unit tests)
    SQLITE_IN_MEMORY_URL: str = "sqlite:///:memory:"


@dataclass(frozen=True)
class TestBlobStorageConfig:
    """Configuration for test blob storage."""

    __test__ = False  # Tell pytest this is not a test class

    # MinIO container settings (for integration tests)
    MINIO_IMAGE: str = "minio/minio:latest"
    MINIO_ACCESS_KEY: str = "test_access_key"
    MINIO_SECRET_KEY: str = "test_secret_key"
    MINIO_BUCKET: str = "test-bucket"

    # File system settings (for unit and integration tests)
    FILE_SYSTEM_BASE_PATH: str = "test_uploads"


@dataclass(frozen=True)
class TestServiceConfig:
    """Configuration for test service instances."""

    __test__ = False  # Tell pytest this is not a test class

    # Default service types for tests
    USER_SERVICE_TYPE: str = "default"
    DOCUMENT_SERVICE_TYPE: str = "default"
    CHAT_SERVICE_TYPE: str = "default"


@dataclass(frozen=True)
class TestRepositoryConfig:
    """Configuration for test repository instances."""

    __test__ = False  # Tell pytest this is not a test class

    # Default repository types for tests
    USER_REPOSITORY_TYPE: str = "sql"
    DOCUMENT_REPOSITORY_TYPE: str = "sql"
    CHAT_SESSION_REPOSITORY_TYPE: str = "sql"
    CHAT_MESSAGE_REPOSITORY_TYPE: str = "sql"


@dataclass(frozen=True)
class TestDataConfig:
    """Configuration for test data and fixtures."""

    __test__ = False  # Tell pytest this is not a test class

    # Sample users data
    SAMPLE_USERNAME: str = "test_user"
    SAMPLE_EMAIL: str = "test@example.com"
    SAMPLE_FULL_NAME: str = "Test User"

    # Sample document data
    SAMPLE_DOCUMENT_NAME: str = "test_document.pdf"
    SAMPLE_TEXT_CONTENT: bytes = b"This is a test document.\nWith multiple lines."

    # Sample chats data
    SAMPLE_CHAT_TITLE: str = "Test Chat Session"
    SAMPLE_CHAT_MESSAGE: str = "Hello, this is a test message"


# Global test configuration instances
# These can be imported and used throughout tests
DB_CONFIG: Final[TestDatabaseConfig] = TestDatabaseConfig()
BLOB_STORAGE_CONFIG: Final[TestBlobStorageConfig] = TestBlobStorageConfig()
SERVICE_CONFIG: Final[TestServiceConfig] = TestServiceConfig()
REPOSITORY_CONFIG: Final[TestRepositoryConfig] = TestRepositoryConfig()
DATA_CONFIG: Final[TestDataConfig] = TestDataConfig()


# Test environment markers
class TestMarkers:
    """Pytest markers for categorizing tests."""

    __test__ = False  # Tell pytest this is not a test class

    UNIT: str = "unit"  # Fast tests with no external dependencies
    INTEGRATION: str = "integration"  # Tests with Docker containers
    SLOW: str = "slow"  # Tests that take more than 1 second
    DATABASE: str = "database"  # Tests requiring database
    BLOB_STORAGE: str = "blob_storage"  # Tests requiring blob storage


# Test timeout settings (in seconds)
class TestTimeouts:
    """Timeout configuration for different test types."""

    __test__ = False  # Tell pytest this is not a test class

    UNIT_TEST_TIMEOUT: int = 5  # Unit tests should complete quickly
    INTEGRATION_TEST_TIMEOUT: int = 30  # Integration tests may take longer
    CONTAINER_STARTUP_TIMEOUT: int = 60  # Time to wait for containers


def get_test_database_url(postgres_host: str, postgres_port: int) -> str:
    """
    Generate test database URL from components.

    Args:
        postgres_host: PostgreSQL container host
        postgres_port: PostgreSQL container port

    Returns:
        str: Full database connection URL
    """
    return (
        f"postgresql://{DB_CONFIG.POSTGRES_USER}:{DB_CONFIG.POSTGRES_PASSWORD}"
        f"@{postgres_host}:{postgres_port}/{DB_CONFIG.POSTGRES_DB}"
    )


def get_test_minio_endpoint(minio_host: str, minio_port: int) -> str:
    """
    Generate test MinIO endpoint URL.

    Args:
        minio_host: MinIO container host
        minio_port: MinIO container port

    Returns:
        str: MinIO endpoint URL
    """
    return f"http://{minio_host}:{minio_port}"
