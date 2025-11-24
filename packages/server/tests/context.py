"""Test context for dependency injection in tests."""

from shared.database.sql import SqlDatabase, PostgresSqlDatabase
from shared.repositories import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    UserRepository,
    create_chat_message_repository,
    create_chat_session_repository,
    create_document_repository,
    create_user_repository,
)
from shared.storage import BlobStorage
from shared.storage.in_memory_blob_storage import InMemoryBlobStorage

from src.domains.chat.service import ChatService
from src.domains.documents.service import DocumentService
from src.domains.users.service import UserService
from src import config


class UnitTestContext:
    """Test context for unit tests using in-memory implementations.

    This context always uses in-memory implementations (InMemoryBlobStorage)
    for fast, isolated unit tests that don't require external dependencies.
    """

    def __init__(self, db_url: str):
        """
        Initialize unit test context with dependencies.

        Args:
            db_url: The database connection URL.
        """
        self.db = PostgresSqlDatabase(db_url)

        # Always use in-memory blob storage for unit tests
        self.blob_storage: BlobStorage = InMemoryBlobStorage()

        # Initialize repositories
        self.user_repository: UserRepository = create_user_repository("postgres", db_url=db_url)
        self.document_repository: DocumentRepository = create_document_repository("postgres", db_url=db_url)
        self.chat_session_repository: ChatSessionRepository = create_chat_session_repository("postgres", db_url=db_url)
        self.chat_message_repository: ChatMessageRepository = create_chat_message_repository("postgres", db_url=db_url)

        # Initialize services with dependency injection
        self.user_service = UserService(repository=self.user_repository)
        self.document_service = DocumentService(
            repository=self.document_repository,
            blob_storage=self.blob_storage,
        )
        self.chat_service = ChatService(
            session_repository=self.chat_session_repository,
            message_repository=self.chat_message_repository,
        )


class IntegrationTestContext:
    """Test context for integration tests using real implementations.

    This context uses real implementations (PostgreSQL via testcontainers,
    MinIO via testcontainers) for integration tests that verify component
    interactions with real databases.
    """

    def __init__(self, db_url: str, blob_storage: BlobStorage):
        """
        Initialize integration test context with dependencies.

        Args:
            db_url: The database connection URL.
            blob_storage: Blob storage instance (should be MinIO from testcontainer)
        """
        self.db = PostgresSqlDatabase(db_url)
        self.blob_storage = blob_storage

        # Initialize repositories
        self.user_repository: UserRepository = create_user_repository("postgres", db_url=db_url)
        self.document_repository: DocumentRepository = create_document_repository("postgres", db_url=db_url)
        self.chat_session_repository: ChatSessionRepository = create_chat_session_repository("postgres", db_url=db_url)
        self.chat_message_repository: ChatMessageRepository = create_chat_message_repository("postgres", db_url=db_url)

        # Initialize services with dependency injection
        self.user_service = UserService(repository=self.user_repository)
        self.document_service = DocumentService(
            repository=self.document_repository,
            blob_storage=self.blob_storage,
        )
        self.chat_service = ChatService(
            session_repository=self.chat_session_repository,
            message_repository=self.chat_message_repository,
        )


def create_unit_test_context(db_url: str) -> UnitTestContext:
    """
    Factory function to create unit test context.

    Args:
        db_url: The database connection URL.

    Returns:
        UnitTestContext: Test context with in-memory implementations
    """
    return UnitTestContext(db_url=db_url)


def create_integration_test_context(
    db_url: str,
    blob_storage: BlobStorage,
) -> IntegrationTestContext:
    """
    Factory function to create integration test context.

    Args:
        db_url: The database connection URL.
        blob_storage: Blob storage instance (should be MinIO from testcontainer)

    Returns:
        IntegrationTestContext: Test context with real implementations
    """
    return IntegrationTestContext(db_url=db_url, blob_storage=blob_storage)
