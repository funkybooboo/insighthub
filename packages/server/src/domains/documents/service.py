"""Document service implementation."""

from dataclasses import dataclass
from typing import BinaryIO

from pypdf import PdfReader
from src.infrastructure.storage import BlobStorage

from .models import Document
from .repositories import DocumentRepository


@dataclass
class DocumentUploadResult:
    """Result of document upload operation."""

    document: Document
    text_length: int
    is_duplicate: bool


class DocumentService:
    """Service for document-related business logic."""

    def __init__(self, repository: DocumentRepository, blob_storage: BlobStorage):
        """
        Initialize service with repository and blob storage.

        Args:
            repository: Document repository implementation
            blob_storage: Blob storage implementation
        """
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
        # BinaryIO.read() always returns bytes, so we just decode it
        return content.decode("utf-8")

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
        chunk_count: int | None = None,
        rag_collection: str | None = None,
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

    def process_document_upload(
        self,
        user_id: int,
        filename: str,
        file_obj: BinaryIO,
    ) -> DocumentUploadResult:
        """
        High-level orchestration method for document upload.

        This method handles the complete document upload workflow including
        MIME type determination, duplicate detection, text extraction, and upload.

        Args:
            user_id: ID of the user uploading the document
            filename: Name of the file
            file_obj: File object (must support seek)

        Returns:
            DocumentUploadResult with document, text length, and duplicate flag
        """
        # Determine MIME type from filename
        extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
        mime_type = "application/pdf" if extension == "pdf" else "text/plain"

        # Check for duplicates
        content_hash = self.calculate_file_hash(file_obj)
        existing_doc = self.get_document_by_hash(content_hash)

        if existing_doc:
            # Document already exists - return it with duplicate flag
            # Extract text for consistency (clients may want text_length)
            file_obj.seek(0)
            text = self.extract_text(file_obj, filename)
            return DocumentUploadResult(
                document=existing_doc,
                text_length=len(text),
                is_duplicate=True,
            )

        # Extract text
        file_obj.seek(0)
        text = self.extract_text(file_obj, filename)

        # Upload document
        file_obj.seek(0)
        document = self.upload_document(
            user_id=user_id,
            filename=filename,
            file_obj=file_obj,
            mime_type=mime_type,
        )

        # TODO: Integrate with RAG system
        # rag_system.add_documents([{"text": text, "metadata": {...}}])
        # Update document.chunk_count and document.rag_collection

        return DocumentUploadResult(
            document=document,
            text_length=len(text),
            is_duplicate=False,
        )

    def download_document(self, document_id: int) -> bytes | None:
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

    def get_document_by_id(self, document_id: int) -> Document | None:
        """Get document by ID."""
        return self.repository.get_by_id(document_id)

    def get_document_by_hash(self, content_hash: str) -> Document | None:
        """Get document by content hash."""
        return self.repository.get_by_content_hash(content_hash)

    def list_user_documents(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """List all documents for a user with pagination."""
        return self.repository.get_by_user(user_id, skip=skip, limit=limit)

    def update_document(self, document_id: int, **kwargs: str | int) -> Document | None:
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
