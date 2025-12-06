"""Integration tests for the DocumentDataAccess component."""

import pytest
from returns.result import Success

from src.domains.workspace.document.data_access import DocumentDataAccess
from src.domains.workspace.document.repositories import DocumentRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase


@pytest.mark.integration
class TestDocumentDataAccessIntegration:
    """Integration tests for the DocumentDataAccess component."""

    @pytest.fixture(scope="function")
    def document_repository(self, db_session: SqlDatabase) -> DocumentRepository:
        """Fixture to create a DocumentRepository."""
        return DocumentRepository(db_session)

    @pytest.fixture(scope="function")
    def data_access_without_cache(
        self, document_repository: DocumentRepository
    ) -> DocumentDataAccess:
        """Fixture for DocumentDataAccess without a cache."""
        return DocumentDataAccess(repository=document_repository, cache=None)

    @pytest.fixture(scope="function")
    def data_access_with_cache(
        self, document_repository: DocumentRepository, cache_instance: RedisCache
    ) -> DocumentDataAccess:
        """Fixture for DocumentDataAccess with a Redis cache."""
        return DocumentDataAccess(repository=document_repository, cache=cache_instance)

    def test_create_and_get_document(
        self, data_access_with_cache: DocumentDataAccess, setup_workspace
    ):
        """Test creating and retrieving a document."""
        # Arrange
        workspace_id = setup_workspace.id

        # Act
        create_result = data_access_with_cache.create(
            workspace_id=workspace_id,
            filename="test.txt",
            file_path="/path/to/test.txt",
            file_size=123,
            mime_type="text/plain",
            content_hash="abc",
            chunk_count=1,
            status="completed",
        )
        assert isinstance(create_result, Success)
        created_document = create_result.unwrap()

        retrieved_document = data_access_with_cache.get_by_id(created_document.id)

        # Assert
        assert retrieved_document is not None
        assert retrieved_document.id == created_document.id
        assert retrieved_document.filename == "test.txt"
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists(f"document:{created_document.id}")

    def test_get_documents_by_workspace(
        self, data_access_with_cache: DocumentDataAccess, setup_workspace
    ):
        """Test retrieving all documents for a workspace."""
        # Arrange
        workspace_id = setup_workspace.id
        data_access_with_cache.create(
            workspace_id=workspace_id,
            filename="test1.txt",
            file_path="/path/to/test1.txt",
            file_size=1,
            mime_type="text/plain",
            content_hash="1",
            chunk_count=1,
            status="completed",
        )
        data_access_with_cache.create(
            workspace_id=workspace_id,
            filename="test2.txt",
            file_path="/path/to/test2.txt",
            file_size=2,
            mime_type="text/plain",
            content_hash="2",
            chunk_count=1,
            status="completed",
        )

        # Act
        documents = data_access_with_cache.get_by_workspace(workspace_id)

        # Assert
        assert len(documents) == 2
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists(f"workspace:{workspace_id}:documents")

    def test_update_document(self, data_access_with_cache: DocumentDataAccess, setup_workspace):
        """Test updating a document."""
        # Arrange
        workspace_id = setup_workspace.id
        create_result = data_access_with_cache.create(
            workspace_id=workspace_id,
            filename="test.txt",
            file_path="/path/to/test.txt",
            file_size=123,
            mime_type="text/plain",
            content_hash="abc",
            chunk_count=1,
            status="processing",
        )
        created_document = create_result.unwrap()

        # Act
        updated = data_access_with_cache.update(
            created_document.id, chunk_count=5, status="completed"
        )

        # Assert
        assert updated is True
        retrieved_document = data_access_with_cache.get_by_id(created_document.id)
        assert retrieved_document is not None
        assert retrieved_document.chunk_count == 5
        assert retrieved_document.status == "completed"

    def test_delete_document(self, data_access_with_cache: DocumentDataAccess, setup_workspace):
        """Test deleting a document."""
        # Arrange
        workspace_id = setup_workspace.id
        create_result = data_access_with_cache.create(
            workspace_id=workspace_id,
            filename="test.txt",
            file_path="/path/to/test.txt",
            file_size=123,
            mime_type="text/plain",
            content_hash="abc",
            chunk_count=1,
            status="completed",
        )
        created_document = create_result.unwrap()
        _ = data_access_with_cache.get_by_id(created_document.id)
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists(f"document:{created_document.id}")

        # Act
        deleted = data_access_with_cache.delete(created_document.id)

        # Assert
        assert deleted is True
        assert data_access_with_cache.cache is not None
        assert not data_access_with_cache.cache.exists(f"document:{created_document.id}")
        assert data_access_with_cache.get_by_id(created_document.id) is None
