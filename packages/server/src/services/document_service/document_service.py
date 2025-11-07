"""Document service interface."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

from src.models import Document


class DocumentService(ABC):
    """Interface for document-related business logic."""

    @abstractmethod
    def calculate_file_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA-256 hash of a file."""
        pass

    @abstractmethod
    def extract_text_from_pdf(self, file_obj: BinaryIO) -> str:
        """Extract text content from a PDF file."""
        pass

    @abstractmethod
    def extract_text_from_txt(self, file_obj: BinaryIO) -> str:
        """Extract text content from a TXT file."""
        pass

    @abstractmethod
    def extract_text(self, file_obj: BinaryIO, filename: str) -> str:
        """Extract text from a document based on its file type."""
        pass

    @abstractmethod
    def upload_document(
        self,
        user_id: int,
        filename: str,
        file_obj: BinaryIO,
        mime_type: str,
        chunk_count: Optional[int] = None,
        rag_collection: Optional[str] = None,
    ) -> Document:
        """Upload a document to blob storage and create database record."""
        pass

    @abstractmethod
    def download_document(self, document_id: int) -> Optional[bytes]:
        """Download document content from blob storage."""
        pass

    @abstractmethod
    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        pass

    @abstractmethod
    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        pass

    @abstractmethod
    def list_user_documents(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Document]:
        """List all documents for a user with pagination."""
        pass

    @abstractmethod
    def update_document(self, document_id: int, **kwargs: str | int) -> Optional[Document]:
        """Update document fields."""
        pass

    @abstractmethod
    def delete_document(self, document_id: int, delete_from_storage: bool = True) -> bool:
        """Delete document by ID."""
        pass
