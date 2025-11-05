"""Unit tests for DocumentService."""

from io import BytesIO

import pytest
from sqlalchemy.orm import Session

from src.db.models import User
from src.db.repository import UserRepository
from src.services.document_service import DocumentService
from src.storage.blob_storage import S3BlobStorage


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user_repo = UserRepository(db_session)
    return user_repo.create(username="testuser", email="test@example.com")


def test_upload_document(
    db_session: Session, blob_storage: S3BlobStorage, test_user: User, sample_text_file: BytesIO
) -> None:
    """Test uploading a document."""
    service = DocumentService(db_session, blob_storage)

    # Upload document
    doc = service.upload_document(
        user_id=test_user.id,
        filename="test.txt",
        file_obj=sample_text_file,
        mime_type="text/plain",
    )

    assert doc.id is not None
    assert doc.filename == "test.txt"
    assert doc.user_id == test_user.id
    assert doc.mime_type == "text/plain"
    assert doc.file_size > 0
    assert doc.content_hash is not None


def test_upload_duplicate_document(
    db_session: Session, blob_storage: S3BlobStorage, test_user: User, sample_text_file: BytesIO
) -> None:
    """Test uploading duplicate document (same hash) creates separate records."""
    service = DocumentService(db_session, blob_storage)

    # Upload same document twice
    doc1 = service.upload_document(
        user_id=test_user.id,
        filename="test1.txt",
        file_obj=sample_text_file,
        mime_type="text/plain",
    )

    sample_text_file.seek(0)
    doc2 = service.upload_document(
        user_id=test_user.id,
        filename="test2.txt",
        file_obj=sample_text_file,
        mime_type="text/plain",
    )

    # Same hash, different records
    assert doc1.content_hash == doc2.content_hash
    assert doc1.id != doc2.id


def test_download_document(
    db_session: Session, blob_storage: S3BlobStorage, test_user: User, sample_text_file: BytesIO
) -> None:
    """Test downloading a document."""
    service = DocumentService(db_session, blob_storage)

    # Upload document
    original_content = sample_text_file.read()
    sample_text_file.seek(0)

    doc = service.upload_document(
        user_id=test_user.id,
        filename="test.txt",
        file_obj=sample_text_file,
        mime_type="text/plain",
    )

    # Download document
    downloaded_content = service.download_document(doc.id)

    assert downloaded_content is not None
    assert downloaded_content == original_content


def test_extract_text_from_txt(
    db_session: Session, blob_storage: S3BlobStorage, sample_text_file: BytesIO
) -> None:
    """Test extracting text from a TXT file."""
    service = DocumentService(db_session, blob_storage)

    text = service.extract_text(sample_text_file, "test.txt")

    assert isinstance(text, str)
    assert "test document" in text.lower()


def test_extract_text_from_pdf(
    db_session: Session, blob_storage: S3BlobStorage, sample_pdf_file: BytesIO
) -> None:
    """Test extracting text from a PDF file."""
    service = DocumentService(db_session, blob_storage)

    text = service.extract_text(sample_pdf_file, "test.pdf")

    assert isinstance(text, str)
    assert "Hello World" in text


def test_calculate_file_hash(
    db_session: Session, blob_storage: S3BlobStorage, sample_text_file: BytesIO
) -> None:
    """Test calculating file hash."""
    service = DocumentService(db_session, blob_storage)

    hash1 = service.calculate_file_hash(sample_text_file)

    # Hash should be consistent
    sample_text_file.seek(0)
    hash2 = service.calculate_file_hash(sample_text_file)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256


def test_list_user_documents(
    db_session: Session, blob_storage: S3BlobStorage, test_user: User
) -> None:
    """Test listing user documents."""
    service = DocumentService(db_session, blob_storage)

    # Upload multiple documents
    file1 = BytesIO(b"content 1")
    file2 = BytesIO(b"content 2")

    service.upload_document(
        user_id=test_user.id,
        filename="doc1.txt",
        file_obj=file1,
        mime_type="text/plain",
    )
    service.upload_document(
        user_id=test_user.id,
        filename="doc2.txt",
        file_obj=file2,
        mime_type="text/plain",
    )

    # List documents
    docs = service.list_user_documents(test_user.id)

    assert len(docs) == 2


def test_delete_document(
    db_session: Session, blob_storage: S3BlobStorage, test_user: User, sample_text_file: BytesIO
) -> None:
    """Test deleting a document."""
    service = DocumentService(db_session, blob_storage)

    # Upload document
    doc = service.upload_document(
        user_id=test_user.id,
        filename="test.txt",
        file_obj=sample_text_file,
        mime_type="text/plain",
    )
    doc_id = doc.id
    blob_key = doc.file_path

    # Verify file exists in storage
    assert blob_storage.file_exists(blob_key) is True

    # Delete document
    result = service.delete_document(doc_id, delete_from_storage=True)

    assert result is True
    assert service.get_document_by_id(doc_id) is None
    assert blob_storage.file_exists(blob_key) is False


def test_update_document(
    db_session: Session, blob_storage: S3BlobStorage, test_user: User, sample_text_file: BytesIO
) -> None:
    """Test updating document metadata."""
    service = DocumentService(db_session, blob_storage)

    # Upload document
    doc = service.upload_document(
        user_id=test_user.id,
        filename="test.txt",
        file_obj=sample_text_file,
        mime_type="text/plain",
    )

    # Update document
    updated_doc = service.update_document(
        doc.id, chunk_count=5, rag_collection="test_collection"
    )

    assert updated_doc is not None
    assert updated_doc.chunk_count == 5
    assert updated_doc.rag_collection == "test_collection"
