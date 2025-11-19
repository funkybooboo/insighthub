"""Unit tests for DocumentRepository."""

import pytest

from shared.models import Document
from shared.repositories import DocumentRepository
from shared.models import User
from shared.repositories import UserRepository


@pytest.fixture
def test_user(user_repository: UserRepository) -> User:
    """Create a test user."""
    return user_repository.create(
        username="testuser", email="test@example.com", password="password123"
    )


def test_create_document(document_repository: DocumentRepository, test_user: User) -> None:
    """Test creating a new document."""
    repo = document_repository

    doc = repo.create(
        user_id=test_user.id,
        filename="test.pdf",
        file_path="blob/key/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="abc123hash",
    )

    assert doc.id is not None
    assert doc.user_id == test_user.id
    assert doc.filename == "test.pdf"
    assert doc.file_path == "blob/key/test.pdf"
    assert doc.file_size == 1024
    assert doc.mime_type == "application/pdf"
    assert doc.content_hash == "abc123hash"
    assert doc.created_at is not None


def test_get_document_by_id(document_repository: DocumentRepository, test_user: User) -> None:
    """Test retrieving a document by ID."""
    repo = document_repository

    # Create document
    created_doc = repo.create(
        user_id=test_user.id,
        filename="test.pdf",
        file_path="blob/key/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="abc123",
    )

    # Retrieve document
    retrieved_doc = repo.get_by_id(created_doc.id)

    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id
    assert retrieved_doc.filename == "test.pdf"


def test_get_documents_by_user(document_repository: DocumentRepository, test_user: User) -> None:
    """Test retrieving all documents for a user."""
    repo = document_repository

    # Create multiple documents
    repo.create(
        user_id=test_user.id,
        filename="doc1.pdf",
        file_path="blob/doc1.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="hash1",
    )
    repo.create(
        user_id=test_user.id,
        filename="doc2.txt",
        file_path="blob/doc2.txt",
        file_size=512,
        mime_type="text/plain",
        content_hash="hash2",
    )

    # Retrieve documents
    docs = repo.get_by_user(test_user.id)

    assert len(docs) == 2
    assert all(isinstance(doc, Document) for doc in docs)
    assert all(doc.user_id == test_user.id for doc in docs)


def test_get_document_by_content_hash(
    document_repository: DocumentRepository, test_user: User
) -> None:
    """Test retrieving a document by content hash."""
    repo = document_repository

    # Create document
    repo.create(
        user_id=test_user.id,
        filename="test.pdf",
        file_path="blob/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="unique_hash_123",
    )

    # Retrieve by hash
    doc = repo.get_by_content_hash("unique_hash_123")

    assert doc is not None
    assert doc.content_hash == "unique_hash_123"


def test_update_document(document_repository: DocumentRepository, test_user: User) -> None:
    """Test updating a document."""
    repo = document_repository

    # Create document
    doc = repo.create(
        user_id=test_user.id,
        filename="test.pdf",
        file_path="blob/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="hash",
    )

    # Update document
    updated_doc = repo.update(doc.id, chunk_count=10, rag_collection="test_collection")

    assert updated_doc is not None
    assert updated_doc.chunk_count == 10
    assert updated_doc.rag_collection == "test_collection"


def test_delete_document(document_repository: DocumentRepository, test_user: User) -> None:
    """Test deleting a document."""
    repo = document_repository

    # Create document
    doc = repo.create(
        user_id=test_user.id,
        filename="test.pdf",
        file_path="blob/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content_hash="hash",
    )
    doc_id = doc.id

    # Delete document
    result = repo.delete(doc_id)

    assert result is True
    assert repo.get_by_id(doc_id) is None


def test_delete_nonexistent_document(document_repository: DocumentRepository) -> None:
    """Test deleting a document that doesn't exist."""
    repo = document_repository

    result = repo.delete(99999)

    assert result is False
