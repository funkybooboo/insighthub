"""Document service for business logic."""

import hashlib
from io import BytesIO
from typing import BinaryIO, Optional

from pypdf import PdfReader

from src.db.interfaces import DocumentRepository
from src.db.models import Document
from src.storage.blob_storage import BlobStorage


class DocumentService:
    """Service for document-related business logic."""

    def __init__(self, repository: DocumentRepository, blob_storage: BlobStorage):
        self.repository = repository
        self.blob_storage = blob_storage

    def calculate_file_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA-256 hash of a file."""
        return self.blob_storage.calculate_hash(file_obj)

    def extract_text_from_pdf(self, file_obj: BinaryIO) -> str:
        """Extract text content from a PDF file."""
        reader = PdfReader(file_obj)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n".join(text_parts)

    def extract_text_from_txt(self, file_obj: BinaryIO) -> str:
        """Extract text content from a TXT file."""
        file_obj.seek(0)
        content = file_obj.read()
        if isinstance(content, bytes):
            return content.decode("utf-8")
        return content

    def extract_text(self, file_obj: BinaryIO, filename: str) -> str:
        """Extract text from a document based on its file type."""
        extension = filename.rsplit(".", 1)[1].lower()
        file_obj.seek(0)
        if extension == "pdf":
            return self.extract_text_from_pdf(file_obj)
        elif extension == "txt":
            return self.extract_text_from_txt(file_obj)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def upload_document(
        self,
        user_id: int,
        filename: str,
        file_obj: BinaryIO,
        mime_type: str,
        chunk_count: Optional[int] = None,
        rag_collection: Optional[str] = None,
    ) -> Document:
        """
        Upload a document to blob storage and create database record.

        Args:
            user_id: User ID uploading the document
            filename: Original filename
            file_obj: File-like object to upload
            mime_type: MIME type of the file
            chunk_count: Optional number of chunks created by RAG
            rag_collection: Optional RAG collection name

        Returns:
            Document: Created document record
        """
        # Calculate hash and file size
        content_hash = self.calculate_file_hash(file_obj)
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(0)  # Reset to beginning

        # Generate blob key (using hash + original filename for uniqueness)
        blob_key = f"{content_hash}/{filename}"

        # Upload to blob storage
        self.blob_storage.upload_file(file_obj, blob_key)

        # Create database record
        return self.repository.create(
            user_id=user_id,
            filename=filename,
            file_path=blob_key,  # Store blob key as file_path
            file_size=file_size,
            mime_type=mime_type,
            content_hash=content_hash,
            chunk_count=chunk_count,
            rag_collection=rag_collection,
        )

    def download_document(self, document_id: int) -> Optional[bytes]:
        """
        Download document content from blob storage.

        Args:
            document_id: The document ID to download

        Returns:
            Optional[bytes]: File content if found, None otherwise
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            return None

        try:
            return self.blob_storage.download_file(document.file_path)
        except Exception as e:
            print(f"Error downloading document: {e}")
            return None

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self.repository.get_by_id(document_id)

    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        return self.repository.get_by_content_hash(content_hash)

    def list_user_documents(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Document]:
        """List all documents for a user with pagination."""
        return self.repository.get_by_user(user_id, skip=skip, limit=limit)

    def update_document(self, document_id: int, **kwargs: str | int) -> Optional[Document]:
        """Update document fields."""
        return self.repository.update(document_id, **kwargs)

    def delete_document(self, document_id: int, delete_from_storage: bool = True) -> bool:
        """
        Delete document by ID.

        Args:
            document_id: The document ID to delete
            delete_from_storage: Whether to also delete from blob storage

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if delete_from_storage:
            document = self.repository.get_by_id(document_id)
            if document:
                try:
                    self.blob_storage.delete_file(document.file_path)
                except Exception as e:
                    print(f"Error deleting from blob storage: {e}")

        return self.repository.delete(document_id)
