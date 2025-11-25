"""Unit tests for DocumentRepository interface and implementations."""

from datetime import datetime
from typing import Optional

import pytest

from shared.models.document import Document
from shared.repositories.document.document_repository import DocumentRepository


class DummyDocumentRepository(DocumentRepository):
    """Dummy implementation of DocumentRepository for testing."""

    def __init__(self) -> None:
        """Initialize with in-memory storage."""
        self.documents: dict[int, Document] = {}
        self.next_id = 1

    def create(
        self,
        user_id: int,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        content_hash: str,
        workspace_id: int | None = None,
        chunk_count: int | None = None,
        rag_collection: str | None = None,
    ) -> Document:
        """Create a new document."""
        doc = Document(
            id=self.next_id,
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            content_hash=content_hash,
            workspace_id=workspace_id,
            chunk_count=chunk_count,
            rag_collection=rag_collection,
        )
        self.documents[doc.id] = doc
        self.next_id += 1
        return doc

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self.documents.get(document_id)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[Document]:
        """Get documents by user ID with pagination."""
        user_docs = [doc for doc in self.documents.values() if doc.user_id == user_id]
        return user_docs[skip : skip + limit]

    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        for doc in self.documents.values():
            if doc.content_hash == content_hash:
                return doc
        return None

    def update(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document fields."""
        doc = self.documents.get(document_id)
        if not doc:
            return None

        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)

        return doc

    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False

    def get_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
    ) -> list[Document]:
        """Get documents by workspace ID with pagination and optional status filter."""
        workspace_docs = [
            doc for doc in self.documents.values()
            if doc.workspace_id == workspace_id and
            (status_filter is None or doc.processing_status == status_filter)
        ]
        return workspace_docs[skip : skip + limit]

    def count_by_workspace(self, workspace_id: int, status_filter: str | None = None) -> int:
        """Count documents in a workspace with optional status filter."""
        return len([
            doc for doc in self.documents.values()
            if doc.workspace_id == workspace_id and
            (status_filter is None or doc.processing_status == status_filter)
        ])


@pytest.fixture
def repository() -> DummyDocumentRepository:
    """Provide a dummy document repository."""
    return DummyDocumentRepository()


class TestDocumentRepositoryCreate:
    """Tests for document creation."""

    def test_create_document_returns_document_with_correct_fields(self, repository: DummyDocumentRepository) -> None:
        """create returns Document with correct fields."""
        doc = repository.create(
            user_id=1,
            filename="test.pdf",
            file_path="/storage/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            content_hash="abc123",
            workspace_id=5,
            chunk_count=10,
            rag_collection="test_collection"
        )

        assert doc.id == 1
        assert doc.user_id == 1
        assert doc.filename == "test.pdf"
        assert doc.file_path == "/storage/test.pdf"
        assert doc.file_size == 1024
        assert doc.mime_type == "application/pdf"
        assert doc.content_hash == "abc123"
        assert doc.workspace_id == 5
        assert doc.chunk_count == 10
        assert doc.rag_collection == "test_collection"

    def test_create_document_with_minimal_fields(self, repository: DummyDocumentRepository) -> None:
        """create handles minimal required fields."""
        doc = repository.create(
            user_id=1,
            filename="test.txt",
            file_path="/storage/test.txt",
            file_size=100,
            mime_type="text/plain",
            content_hash="hash123"
        )

        assert doc.workspace_id is None
        assert doc.chunk_count is None
        assert doc.rag_collection is None

    def test_create_document_assigns_unique_ids(self, repository: DummyDocumentRepository) -> None:
        """create assigns unique IDs to documents."""
        doc1 = repository.create(1, "file1.pdf", "/path1", 100, "application/pdf", "hash1")
        doc2 = repository.create(1, "file2.pdf", "/path2", 200, "application/pdf", "hash2")

        assert doc1.id == 1
        assert doc2.id == 2
        assert doc1.id != doc2.id

    def test_create_document_stores_document(self, repository: DummyDocumentRepository) -> None:
        """create stores document for later retrieval."""
        created = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "hash")

        retrieved = repository.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id


class TestDocumentRepositoryGetById:
    """Tests for get_by_id method."""

    def test_get_by_id_returns_correct_document(self, repository: DummyDocumentRepository) -> None:
        """get_by_id returns correct document when exists."""
        created = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "hash")

        result = repository.get_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.filename == "test.pdf"

    def test_get_by_id_returns_none_when_not_exists(self, repository: DummyDocumentRepository) -> None:
        """get_by_id returns None when document doesn't exist."""
        result = repository.get_by_id(999)

        assert result is None


class TestDocumentRepositoryGetByUser:
    """Tests for get_by_user method."""

    def test_get_by_user_returns_user_documents(self, repository: DummyDocumentRepository) -> None:
        """get_by_user returns only documents belonging to specified user."""
        # Create documents for different users
        doc1 = repository.create(1, "user1_file1.pdf", "/path1", 100, "application/pdf", "hash1")
        doc2 = repository.create(1, "user1_file2.pdf", "/path2", 200, "application/pdf", "hash2")
        doc3 = repository.create(2, "user2_file.pdf", "/path3", 300, "application/pdf", "hash3")

        result = repository.get_by_user(1)

        assert len(result) == 2
        assert doc1 in result
        assert doc2 in result
        assert doc3 not in result

    def test_get_by_user_returns_empty_list_when_no_documents(self, repository: DummyDocumentRepository) -> None:
        """get_by_user returns empty list when user has no documents."""
        result = repository.get_by_user(1)

        assert result == []

    def test_get_by_user_with_pagination(self, repository: DummyDocumentRepository) -> None:
        """get_by_user handles pagination correctly."""
        # Create multiple documents for user
        for i in range(5):
            repository.create(1, f"file{i}.pdf", f"/path{i}", 100, "application/pdf", f"hash{i}")

        result = repository.get_by_user(1, skip=2, limit=2)

        assert len(result) == 2
        assert result[0].filename == "file2.pdf"
        assert result[1].filename == "file3.pdf"


class TestDocumentRepositoryGetByContentHash:
    """Tests for get_by_content_hash method."""

    def test_get_by_content_hash_returns_correct_document(self, repository: DummyDocumentRepository) -> None:
        """get_by_content_hash returns correct document when exists."""
        created = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "unique_hash")

        result = repository.get_by_content_hash("unique_hash")

        assert result is not None
        assert result.id == created.id
        assert result.content_hash == "unique_hash"

    def test_get_by_content_hash_returns_none_when_not_exists(self, repository: DummyDocumentRepository) -> None:
        """get_by_content_hash returns None when hash doesn't exist."""
        result = repository.get_by_content_hash("nonexistent_hash")

        assert result is None

    def test_get_by_content_hash_handles_duplicates(self, repository: DummyDocumentRepository) -> None:
        """get_by_content_hash returns first document when multiple have same hash."""
        # This shouldn't happen in practice, but test the behavior
        doc1 = repository.create(1, "file1.pdf", "/path1", 100, "application/pdf", "same_hash")
        doc2 = repository.create(2, "file2.pdf", "/path2", 200, "application/pdf", "same_hash")

        result = repository.get_by_content_hash("same_hash")

        # Should return one of them (implementation dependent which one)
        assert result is not None
        assert result.content_hash == "same_hash"


class TestDocumentRepositoryUpdate:
    """Tests for update method."""

    def test_update_existing_document(self, repository: DummyDocumentRepository) -> None:
        """update modifies existing document fields."""
        doc = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "hash")

        updated = repository.update(doc.id, filename="updated.pdf", file_size=200)

        assert updated is not None
        assert updated.id == doc.id
        assert updated.filename == "updated.pdf"
        assert updated.file_size == 200

    def test_update_nonexistent_document(self, repository: DummyDocumentRepository) -> None:
        """update returns None for nonexistent document."""
        result = repository.update(999, filename="updated.pdf")

        assert result is None

    def test_update_processing_status(self, repository: DummyDocumentRepository) -> None:
        """update can modify processing status."""
        doc = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "hash")

        updated = repository.update(doc.id, processing_status="ready")

        assert updated is not None
        assert updated.processing_status == "ready"


class TestDocumentRepositoryDelete:
    """Tests for delete method."""

    def test_delete_existing_document(self, repository: DummyDocumentRepository) -> None:
        """delete removes existing document."""
        doc = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "hash")

        result = repository.delete(doc.id)

        assert result is True
        assert repository.get_by_id(doc.id) is None

    def test_delete_nonexistent_document(self, repository: DummyDocumentRepository) -> None:
        """delete returns False for nonexistent document."""
        result = repository.delete(999)

        assert result is False


class TestDocumentRepositoryGetByWorkspace:
    """Tests for get_by_workspace method."""

    def test_get_by_workspace_returns_workspace_documents(self, repository: DummyDocumentRepository) -> None:
        """get_by_workspace returns only documents in specified workspace."""
        # Create documents in different workspaces
        doc1 = repository.create(1, "file1.pdf", "/path1", 100, "application/pdf", "hash1", workspace_id=1)
        doc2 = repository.create(1, "file2.pdf", "/path2", 200, "application/pdf", "hash2", workspace_id=1)
        doc3 = repository.create(2, "file3.pdf", "/path3", 300, "application/pdf", "hash3", workspace_id=2)

        result = repository.get_by_workspace(1)

        assert len(result) == 2
        assert doc1 in result
        assert doc2 in result
        assert doc3 not in result

    def test_get_by_workspace_with_status_filter(self, repository: DummyDocumentRepository) -> None:
        """get_by_workspace filters by processing status."""
        doc1 = repository.create(1, "file1.pdf", "/path1", 100, "application/pdf", "hash1", workspace_id=1)
        doc2 = repository.create(1, "file2.pdf", "/path2", 200, "application/pdf", "hash2", workspace_id=1)

        # Update one document to ready status
        repository.update(doc1.id, processing_status="ready")
        repository.update(doc2.id, processing_status="processing")

        result = repository.get_by_workspace(1, status_filter="ready")

        assert len(result) == 1
        assert result[0].id == doc1.id

    def test_get_by_workspace_with_pagination(self, repository: DummyDocumentRepository) -> None:
        """get_by_workspace handles pagination."""
        # Create multiple documents in workspace
        docs = []
        for i in range(5):
            doc = repository.create(1, f"file{i}.pdf", f"/path{i}", 100, "application/pdf", f"hash{i}", workspace_id=1)
            docs.append(doc)

        result = repository.get_by_workspace(1, skip=2, limit=2)

        assert len(result) == 2
        assert result[0].id == docs[2].id
        assert result[1].id == docs[3].id


class TestDocumentRepositoryCountByWorkspace:
    """Tests for count_by_workspace method."""

    def test_count_by_workspace_returns_correct_count(self, repository: DummyDocumentRepository) -> None:
        """count_by_workspace returns correct count of documents in workspace."""
        # Create documents in different workspaces
        repository.create(1, "file1.pdf", "/path1", 100, "application/pdf", "hash1", workspace_id=1)
        repository.create(1, "file2.pdf", "/path2", 200, "application/pdf", "hash2", workspace_id=1)
        repository.create(2, "file3.pdf", "/path3", 300, "application/pdf", "hash3", workspace_id=2)

        count = repository.count_by_workspace(1)

        assert count == 2

    def test_count_by_workspace_with_status_filter(self, repository: DummyDocumentRepository) -> None:
        """count_by_workspace filters by processing status."""
        doc1 = repository.create(1, "file1.pdf", "/path1", 100, "application/pdf", "hash1", workspace_id=1)
        doc2 = repository.create(1, "file2.pdf", "/path2", 200, "application/pdf", "hash2", workspace_id=1)

        repository.update(doc1.id, processing_status="ready")
        repository.update(doc2.id, processing_status="failed")

        count = repository.count_by_workspace(1, status_filter="ready")

        assert count == 1

    def test_count_by_workspace_empty_workspace(self, repository: DummyDocumentRepository) -> None:
        """count_by_workspace returns 0 for empty workspace."""
        count = repository.count_by_workspace(1)

        assert count == 0


class TestDocumentRepositoryIntegration:
    """Integration tests for multiple operations."""

    def test_create_then_get_by_content_hash(self, repository: DummyDocumentRepository) -> None:
        """create followed by get_by_content_hash works."""
        created = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "unique_hash")
        retrieved = repository.get_by_content_hash("unique_hash")

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_update_processing_status_then_filter_by_workspace(self, repository: DummyDocumentRepository) -> None:
        """update processing status then filter by workspace works."""
        doc = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "hash", workspace_id=1)
        repository.update(doc.id, processing_status="ready")

        ready_docs = repository.get_by_workspace(1, status_filter="ready")

        assert len(ready_docs) == 1
        assert ready_docs[0].id == doc.id
        assert ready_docs[0].processing_status == "ready"

    def test_delete_affects_all_queries(self, repository: DummyDocumentRepository) -> None:
        """delete affects all query methods."""
        doc = repository.create(1, "test.pdf", "/path", 100, "application/pdf", "hash", workspace_id=1)

        # Verify document exists in all queries
        assert repository.get_by_id(doc.id) is not None
        assert len(repository.get_by_user(1)) == 1
        assert len(repository.get_by_workspace(1)) == 1
        assert repository.get_by_content_hash("hash") is not None

        # Delete document
        repository.delete(doc.id)

        # Verify document gone from all queries
        assert repository.get_by_id(doc.id) is None
        assert len(repository.get_by_user(1)) == 0
        assert len(repository.get_by_workspace(1)) == 0
        assert repository.get_by_content_hash("hash") is None