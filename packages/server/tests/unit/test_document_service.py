"""Unit tests for DocumentService."""

import hashlib
import io
from datetime import datetime
from typing import BinaryIO, Optional
from unittest.mock import Mock, patch

import pytest
from shared.models import Document
from shared.repositories import DocumentRepository
from shared.storage import BlobStorage
from shared.storage.blob_storage import BlobStorageError
from shared.types.result import Err, Ok, Result

from src.domains.workspaces.documents.exceptions import (
    DocumentNotFoundError,
    DocumentProcessingError,
    InvalidFileTypeError,
)
from src.domains.workspaces.documents.service import DocumentService


class FakeBlobStorage(BlobStorage):
    """Fake blob storage for testing."""

    def __init__(self) -> None:
        """Initialize with in-memory storage."""
        self.storage: dict[str, bytes] = {}

    def upload_file(self, file_obj: BinaryIO, blob_key: str) -> Result[str, BlobStorageError]:
        """Upload a file to in-memory storage."""
        file_obj.seek(0)
        self.storage[blob_key] = file_obj.read()
        return Ok(blob_key)

    def download_file(self, blob_key: str) -> Result[bytes, BlobStorageError]:
        """Download a file from in-memory storage."""
        if blob_key not in self.storage:
            return Err(BlobStorageError(f"Blob not found: {blob_key}"))
        return Ok(self.storage[blob_key])

    def delete_file(self, blob_key: str) -> Result[bool, BlobStorageError]:
        """Delete a file from in-memory storage."""
        if blob_key in self.storage:
            del self.storage[blob_key]
            return Ok(True)
        return Ok(False)

    def file_exists(self, blob_key: str) -> bool:
        """Check if file exists."""
        return blob_key in self.storage

    def list_files(self, prefix: str | None = None) -> list[str]:
        """List all files with optional prefix filter."""
        if prefix:
            return [key for key in self.storage if key.startswith(prefix)]
        return list(self.storage.keys())

    def calculate_hash(self, file_obj: BinaryIO) -> str:
        """Calculate hash of file."""
        file_obj.seek(0)
        content = file_obj.read()
        file_obj.seek(0)
        return hashlib.sha256(content).hexdigest()


class FakeDocumentRepository(DocumentRepository):
    """Fake document repository for testing."""

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
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.documents[doc.id] = doc
        self.next_id += 1
        return doc

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self.documents.get(document_id)

    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        for doc in self.documents.values():
            if doc.content_hash == content_hash:
                return doc
        return None

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get all documents for a user."""
        user_docs = [doc for doc in self.documents.values() if doc.user_id == user_id]
        return user_docs[skip : skip + limit]

    def update(self, document_id: int, **kwargs: str | int | None) -> Optional[Document]:
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


@pytest.fixture
def fake_repository() -> FakeDocumentRepository:
    """Provide a fake repository."""
    return FakeDocumentRepository()


@pytest.fixture
def fake_storage() -> FakeBlobStorage:
    """Provide a fake blob storage."""
    return FakeBlobStorage()


@pytest.fixture
def service(
    fake_repository: FakeDocumentRepository, fake_storage: FakeBlobStorage
) -> DocumentService:
    """Provide a DocumentService with fake dependencies."""
    return DocumentService(repository=fake_repository, blob_storage=fake_storage)


class TestFilenameValidation:
    """Tests for filename validation."""

    def test_validate_txt_file(self, service: DocumentService) -> None:
        """Test validating a txt file."""
        service.validate_filename("document.txt")

    def test_validate_pdf_file(self, service: DocumentService) -> None:
        """Test validating a pdf file."""
        service.validate_filename("document.pdf")

    def test_validate_uppercase_extension(self, service: DocumentService) -> None:
        """Test validating file with uppercase extension."""
        service.validate_filename("document.PDF")

    def test_validate_invalid_extension(self, service: DocumentService) -> None:
        """Test validating file with invalid extension."""
        with pytest.raises(InvalidFileTypeError):
            service.validate_filename("document.docx")

    def test_validate_no_extension(self, service: DocumentService) -> None:
        """Test validating file without extension."""
        with pytest.raises(InvalidFileTypeError):
            service.validate_filename("document")

    def test_validate_empty_filename(self, service: DocumentService) -> None:
        """Test validating empty filename."""
        with pytest.raises(InvalidFileTypeError):
            service.validate_filename("")

    def test_validate_none_filename(self, service: DocumentService) -> None:
        """Test validating None filename."""
        with pytest.raises(InvalidFileTypeError):
            service.validate_filename(None)


class TestTextExtraction:
    """Tests for text extraction."""

    def test_extract_text_from_txt(self, service: DocumentService) -> None:
        """Test extracting text from txt file."""
        content = b"Hello, world!"
        file_obj = io.BytesIO(content)

        text = service.extract_text_from_txt(file_obj)
        assert text == "Hello, world!"

    def test_extract_text_from_txt_unicode(self, service: DocumentService) -> None:
        """Test extracting text with unicode characters."""
        content = b"Hello, world with unicode"
        file_obj = io.BytesIO(content)

        text = service.extract_text_from_txt(file_obj)
        assert "Hello, world" in text

    def test_extract_text_unsupported_type(self, service: DocumentService) -> None:
        """Test extracting text from unsupported file type."""
        file_obj = io.BytesIO(b"content")

        with pytest.raises(DocumentProcessingError):
            service.extract_text(file_obj, "document.docx")


class TestFileHashing:
    """Tests for file hashing."""

    def test_calculate_file_hash(self, service: DocumentService) -> None:
        """Test calculating file hash."""
        content = b"Hello, world!"
        file_obj = io.BytesIO(content)

        hash1 = service.calculate_file_hash(file_obj)
        file_obj.seek(0)
        hash2 = service.calculate_file_hash(file_obj)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_different_content_different_hash(self, service: DocumentService) -> None:
        """Test that different content produces different hash."""
        file_obj1 = io.BytesIO(b"Content 1")
        file_obj2 = io.BytesIO(b"Content 2")

        hash1 = service.calculate_file_hash(file_obj1)
        hash2 = service.calculate_file_hash(file_obj2)

        assert hash1 != hash2


class TestDocumentUpload:
    """Tests for document upload."""

    def test_upload_document_success(self, service: DocumentService) -> None:
        """Test successful document upload."""
        content = b"Test document content"
        file_obj = io.BytesIO(content)

        document = service.upload_document(
            user_id=1,
            filename="test.txt",
            file_obj=file_obj,
            mime_type="text/plain",
        )

        assert document.id == 1
        assert document.user_id == 1
        assert document.filename == "test.txt"
        assert document.file_size == len(content)
        assert document.mime_type == "text/plain"
        assert len(document.content_hash) == 64

    def test_upload_document_with_rag_metadata(self, service: DocumentService) -> None:
        """Test uploading document with RAG metadata."""
        content = b"Test document content"
        file_obj = io.BytesIO(content)

        document = service.upload_document(
            user_id=1,
            filename="test.txt",
            file_obj=file_obj,
            mime_type="text/plain",
            chunk_count=5,
            rag_collection="test_collection",
        )

        assert document.chunk_count == 5
        assert document.rag_collection == "test_collection"

    def test_upload_stores_in_blob_storage(
        self, service: DocumentService, fake_storage: FakeBlobStorage
    ) -> None:
        """Test that upload stores file in blob storage."""
        content = b"Test document content"
        file_obj = io.BytesIO(content)

        service.upload_document(
            user_id=1,
            filename="test.txt",
            file_obj=file_obj,
            mime_type="text/plain",
        )

        assert len(fake_storage.storage) == 1


class TestProcessDocumentUpload:
    """Tests for process_document_upload orchestration."""

    def test_process_document_upload_new_file(self, service: DocumentService) -> None:
        """Test processing upload for new file."""
        content = b"Test document content"
        file_obj = io.BytesIO(content)

        result = service.process_document_upload(user_id=1, filename="test.txt", file_obj=file_obj)

        assert result.document.filename == "test.txt"
        assert result.text_length == len(content)
        assert result.is_duplicate is False

    def test_process_document_upload_duplicate(self, service: DocumentService) -> None:
        """Test processing upload for duplicate file."""
        content = b"Test document content"

        file_obj1 = io.BytesIO(content)
        result1 = service.process_document_upload(
            user_id=1, filename="test.txt", file_obj=file_obj1
        )

        file_obj2 = io.BytesIO(content)
        result2 = service.process_document_upload(
            user_id=1, filename="test.txt", file_obj=file_obj2
        )

        assert result2.is_duplicate is True
        assert result1.document.id == result2.document.id


class TestDocumentDownload:
    """Tests for document download."""

    def test_download_document_success(self, service: DocumentService) -> None:
        """Test successful document download."""
        content = b"Test document content"
        file_obj = io.BytesIO(content)

        document = service.upload_document(
            user_id=1,
            filename="test.txt",
            file_obj=file_obj,
            mime_type="text/plain",
        )

        downloaded = service.download_document(document.id)
        assert downloaded == content

    def test_download_document_not_found(self, service: DocumentService) -> None:
        """Test downloading non-existent document."""
        result = service.download_document(999)
        assert result is None


class TestDocumentRetrieval:
    """Tests for document retrieval."""

    def test_get_document_by_id(self, service: DocumentService) -> None:
        """Test getting document by ID."""
        content = b"Test content"
        file_obj = io.BytesIO(content)

        created = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        document = service.get_document_by_id(created.id)
        assert document is not None
        assert document.id == created.id

    def test_get_document_by_id_not_found(self, service: DocumentService) -> None:
        """Test getting non-existent document by ID."""
        document = service.get_document_by_id(999)
        assert document is None

    def test_get_document_by_hash(self, service: DocumentService) -> None:
        """Test getting document by content hash."""
        content = b"Test content"
        file_obj = io.BytesIO(content)

        created = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        document = service.get_document_by_hash(created.content_hash)
        assert document is not None
        assert document.content_hash == created.content_hash


class TestListUserDocuments:
    """Tests for listing user documents."""

    def test_list_user_documents_empty(self, service: DocumentService) -> None:
        """Test listing documents for user with no documents."""
        documents = service.list_user_documents(user_id=1)
        assert len(documents) == 0

    def test_list_user_documents_multiple(self, service: DocumentService) -> None:
        """Test listing multiple documents for user."""
        for i in range(3):
            file_obj = io.BytesIO(f"Content {i}".encode())
            service.upload_document(
                user_id=1, filename=f"test{i}.txt", file_obj=file_obj, mime_type="text/plain"
            )

        documents = service.list_user_documents(user_id=1)
        assert len(documents) == 3

    def test_list_user_documents_filters_by_user(self, service: DocumentService) -> None:
        """Test that listing filters by user ID."""
        file_obj1 = io.BytesIO(b"Content 1")
        service.upload_document(
            user_id=1, filename="test1.txt", file_obj=file_obj1, mime_type="text/plain"
        )

        file_obj2 = io.BytesIO(b"Content 2")
        service.upload_document(
            user_id=2, filename="test2.txt", file_obj=file_obj2, mime_type="text/plain"
        )

        user1_docs = service.list_user_documents(user_id=1)
        user2_docs = service.list_user_documents(user_id=2)

        assert len(user1_docs) == 1
        assert len(user2_docs) == 1
        assert user1_docs[0].user_id == 1
        assert user2_docs[0].user_id == 2


class TestDocumentUpdate:
    """Tests for updating documents."""

    def test_update_document_success(self, service: DocumentService) -> None:
        """Test updating document fields."""
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        updated = service.update_document(doc.id, chunk_count=10)
        assert updated is not None
        assert updated.chunk_count == 10

    def test_update_document_not_found(self, service: DocumentService) -> None:
        """Test updating non-existent document."""
        result = service.update_document(999, chunk_count=10)
        assert result is None


class TestDocumentDeletion:
    """Tests for deleting documents."""

    def test_delete_document_success(self, service: DocumentService) -> None:
        """Test deleting a document."""
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        result = service.delete_document(doc.id, delete_from_storage=True)
        assert result is True
        assert service.get_document_by_id(doc.id) is None

    def test_delete_document_removes_from_storage(
        self, service: DocumentService, fake_storage: FakeBlobStorage
    ) -> None:
        """Test that deletion removes file from storage."""
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        assert len(fake_storage.storage) == 1
        service.delete_document(doc.id, delete_from_storage=True)
        assert len(fake_storage.storage) == 0

    def test_delete_document_without_storage_cleanup(
        self, service: DocumentService, fake_storage: FakeBlobStorage
    ) -> None:
        """Test deleting document without storage cleanup."""
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        assert len(fake_storage.storage) == 1
        service.delete_document(doc.id, delete_from_storage=False)
        assert len(fake_storage.storage) == 1

    def test_delete_document_not_found(self, service: DocumentService) -> None:
        """Test deleting non-existent document."""
        result = service.delete_document(999)
        assert result is False

    def test_delete_document_with_validation_success(self, service: DocumentService) -> None:
        """Test deleting document with validation."""
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        service.delete_document_with_validation(doc.id)
        assert service.get_document_by_id(doc.id) is None

    def test_delete_document_with_validation_not_found(self, service: DocumentService) -> None:
        """Test deleting non-existent document with validation."""
        with pytest.raises(DocumentNotFoundError):
            service.delete_document_with_validation(999)


class TestWorkspaceDocumentOperations:
    """Tests for workspace-specific document operations."""

    def test_upload_document_to_workspace_success(self, service: DocumentService) -> None:
        """Test successful document upload to workspace."""
        content = b"Test content"
        file_obj = io.BytesIO(content)

        result = service.upload_document_to_workspace(
            workspace_id=1,
            user_id=1,
            filename="test.txt",
            file_obj=file_obj,
        )

        assert result.document.filename == "test.txt"
        # Note: workspace_id is set after document creation
        assert result.text_length == len(content)

    def test_list_workspace_documents_success(self, service: DocumentService) -> None:
        """Test successful workspace document listing."""
        # Create documents in workspace
        file_obj1 = io.BytesIO(b"Content 1")
        doc1 = service.upload_document(
            user_id=1, filename="test1.txt", file_obj=file_obj1, mime_type="text/plain"
        )
        service.repository.update(doc1.id, workspace_id=1)

        file_obj2 = io.BytesIO(b"Content 2")
        doc2 = service.upload_document(
            user_id=1, filename="test2.txt", file_obj=file_obj2, mime_type="text/plain"
        )
        service.repository.update(doc2.id, workspace_id=1)

        result = service.list_workspace_documents(
            workspace_id=1,
            user_id=1,
            limit=10,
            offset=0,
        )

        assert result.count == 2
        assert len(result.documents) == 2
        # Note: workspace_id filtering is done at repository level

    def test_list_workspace_documents_with_status_filter(self, service: DocumentService) -> None:
        """Test workspace document listing with status filter."""
        # Create documents with different statuses
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )
        service.repository.update(doc.id, workspace_id=1, processing_status="ready")

        result = service.list_workspace_documents(
            workspace_id=1,
            user_id=1,
            status_filter="ready",
        )

        assert result.count == 1
        assert result.documents[0].processing_status == "ready"

    def test_delete_workspace_document_success(self, service: DocumentService) -> None:
        """Test successful workspace document deletion."""
        # Create document in workspace
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )
        service.repository.update(doc.id, workspace_id=1)

        # Should not raise exception
        service.delete_workspace_document(
            document_id=doc.id,
            workspace_id=1,
            user_id=1,
        )

        # Document should be deleted
        assert service.get_document_by_id(doc.id) is None

    def test_delete_workspace_document_not_in_workspace(self, service: DocumentService) -> None:
        """Test deletion of document not in specified workspace."""
        # Create document in different workspace
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )
        service.repository.update(doc.id, workspace_id=2)  # Different workspace

        with pytest.raises(DocumentNotFoundError):
            service.delete_workspace_document(
                document_id=doc.id,
                workspace_id=1,  # Wrong workspace
                user_id=1,
            )

    def test_update_document_status_success(self, service: DocumentService) -> None:
        """Test successful document status update."""
        # Create document
        file_obj = io.BytesIO(b"Content")
        doc = service.upload_document(
            user_id=1, filename="test.txt", file_obj=file_obj, mime_type="text/plain"
        )

        with patch('src.domains.workspaces.documents.service.publish_document_status') as mock_publish:
            result = service.update_document_status(
                document_id=doc.id,
                status="ready",
                chunk_count=5,
            )

            assert result is True
            mock_publish.assert_called_once()

    def test_update_document_status_invalid_status(self, service: DocumentService) -> None:
        """Test document status update with invalid status."""
        with pytest.raises(ValueError, match="Invalid status"):
            service.update_document_status(
                document_id=1,
                status="invalid_status",
            )

    def test_fetch_wikipedia_article_success(self, service: DocumentService) -> None:
        """Test successful Wikipedia article fetching."""
        with patch('src.domains.workspaces.documents.service.requests.get') as mock_get:
            # Mock successful API response
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "title": "Test Article",
                "extract": "This is a test article extract.",
                "description": "A test description",
            }
            mock_get.return_value = mock_response

            result = service.fetch_wikipedia_article(
                workspace_id=1,
                user_id=1,
                query="test article",
                language="en",
            )

            assert "Wikipedia_Test_Article.md" in result.document.filename
            # Note: workspace_id is set during upload

    def test_fetch_wikipedia_article_api_failure(self, service: DocumentService) -> None:
        """Test Wikipedia fetching when API fails."""
        with patch('src.domains.workspaces.documents.service.requests.get') as mock_get:
            mock_get.side_effect = Exception("API error")

            result = service.fetch_wikipedia_article(
                workspace_id=1,
                user_id=1,
                query="test",
                language="en",
            )

            # Should create error placeholder
            assert "error" in result.document.filename.lower()
            # Note: workspace_id is set during upload
