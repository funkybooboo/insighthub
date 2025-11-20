"""Document service implementation."""

from dataclasses import dataclass
from typing import BinaryIO

from pypdf import PdfReader
from shared.messaging import RabbitMQPublisher
from shared.models import Document
from shared.repositories import DocumentRepository
from shared.storage import BlobStorage

from .dtos import DocumentListResponse, DocumentUploadResponse
from .exceptions import DocumentNotFoundError, DocumentProcessingError, InvalidFileTypeError
from .mappers import DocumentMapper


@dataclass
class DocumentUploadResult:
    """Result of document upload operation."""

    document: Document
    text_length: int
    is_duplicate: bool


ALLOWED_EXTENSIONS = {"txt", "pdf"}


class DocumentService:
    """Service for document-related business logic."""

    def __init__(
        self,
        repository: DocumentRepository,
        blob_storage: BlobStorage,
        message_publisher: RabbitMQPublisher | None = None,
    ):
        """
        Initialize service with repository and blob storage.

        Args:
            repository: Document repository implementation
            blob_storage: Blob storage implementation
            message_publisher: Optional RabbitMQ publisher for event publishing
        """
        self.repository = repository
        self.blob_storage = blob_storage
        self.message_publisher = message_publisher

    def validate_filename(self, filename: str | None) -> None:
        """
        Validate that a filename has an allowed extension.

        Args:
            filename: The filename to validate

        Raises:
            InvalidFileTypeError: If filename validation fails
        """
        if not filename:
            raise InvalidFileTypeError("", ALLOWED_EXTENSIONS)

        if "." not in filename:
            raise InvalidFileTypeError(filename, ALLOWED_EXTENSIONS)

        extension = filename.rsplit(".", 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(filename, ALLOWED_EXTENSIONS)

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
        """
        Extract text from a document based on its file type.

        Args:
            file_obj: File-like object
            filename: Original filename

        Returns:
            Extracted text content

        Raises:
            DocumentProcessingError: If text extraction fails
        """
        try:
            extension = filename.rsplit(".", 1)[1].lower()
            file_obj.seek(0)
            if extension == "pdf":
                return self.extract_text_from_pdf(file_obj)
            elif extension == "txt":
                return self.extract_text_from_txt(file_obj)
            else:
                raise DocumentProcessingError(filename, f"Unsupported file type: {extension}")
        except DocumentProcessingError:
            raise
        except Exception as e:
            raise DocumentProcessingError(filename, str(e)) from e

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

        # Publish document.uploaded event to RabbitMQ for async processing
        if self.message_publisher:
            try:
                self.message_publisher.publish(
                    routing_key="document.uploaded",
                    message={
                        "document_id": document.id,
                        "user_id": user_id,
                        "filename": filename,
                        "file_path": document.file_path,
                        "mime_type": mime_type,
                        "text": text,
                        "text_length": len(text),
                        "uploaded_at": document.created_at.isoformat(),
                    },
                )
            except Exception as e:
                # TODO: Add proper error handling
                # Options:
                # 1. Log error and continue (async processing will be skipped)
                # 2. Raise exception and rollback upload
                # 3. Retry with exponential backoff
                print(f"Warning: Failed to publish document.uploaded event: {e}")

        # TODO: RAG INTEGRATION - Async Processing
        # The above RabbitMQ event will trigger the ingestion worker which uses
        # shared.orchestrators.vector_rag.VectorRAGIndexer to process the document.
        #
        # The flow is:
        # 1. Server uploads file to MinIO and creates DB record
        # 2. Server publishes 'document.uploaded' event
        # 3. Ingestion worker consumes event
        # 4. Ingestion worker downloads file and uses VectorRAGIndexer.ingest()
        # 5. VectorRAGIndexer handles parsing, chunking, embedding, and indexing

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

    def upload_document_with_user(
        self,
        user_id: int,
        filename: str,
        file_obj: BinaryIO,
    ) -> DocumentUploadResponse:
        """
        High-level method for document upload that returns a DTO.

        This method handles validation, duplicate detection, upload,
        and formats the response.

        Args:
            user_id: ID of the user uploading the document
            filename: Name of the file
            file_obj: File object (must support seek)

        Returns:
            DocumentUploadResponse DTO ready for JSON serialization

        Raises:
            InvalidFileTypeError: If validation fails
            DocumentProcessingError: If document processing fails
        """
        # Validate filename (raises exception if invalid)
        self.validate_filename(filename)

        # Process upload
        result = self.process_document_upload(
            user_id=user_id,
            filename=filename,
            file_obj=file_obj,
        )

        # Build response message
        message = (
            "Document already exists" if result.is_duplicate else "Document uploaded successfully"
        )

        # Convert to DTO
        return DocumentUploadResponse(
            message=message,
            document=DocumentMapper.document_to_dto(result.document),
            text_length=result.text_length,
        )

    def list_user_documents_as_dto(self, user_id: int) -> DocumentListResponse:
        """
        List all documents for a user as a DTO.

        Args:
            user_id: The user ID

        Returns:
            DocumentListResponse DTO ready for JSON serialization
        """
        documents = self.list_user_documents(user_id)
        document_dtos = DocumentMapper.documents_to_dtos(documents)

        return DocumentListResponse(
            documents=document_dtos,
            count=len(document_dtos),
        )

    def delete_document_with_validation(self, document_id: int) -> None:
        """
        Delete a document with validation.

        Args:
            document_id: The document ID to delete

        Raises:
            DocumentNotFoundError: If document does not exist
        """
        # Check if document exists
        document = self.get_document_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(document_id)

        # TODO: RAG INTEGRATION - Document Removal
        # Before deleting document from database, remove it from RAG system
        #
        # Implementation steps:
        # 1. Publish 'document.deleted' event
        # 2. Workers consume event and delete chunks/vectors/nodes
        #
        # Legacy sync approach (for reference):
        #    from src.rag.factory import create_rag
        #    rag = create_rag(...)
        #    rag.remove_document(document_id)

        # Delete document (includes blob storage cleanup)
        self.delete_document(document_id, delete_from_storage=True)
