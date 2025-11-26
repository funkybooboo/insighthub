"""Document service implementation."""

import hashlib
from typing import BinaryIO

from src.infrastructure.models import Document
from src.infrastructure.repositories.documents import DocumentRepository
from src.infrastructure.storage import BlobStorage

from .dtos import DocumentListResponse, DocumentUploadResult
from .exceptions import DocumentNotFoundError, DocumentProcessingError
from .mappers import DocumentMapper


# Allowed extensions are determined dynamically from registered parsers
def get_allowed_extensions() -> set[str]:
    """Get allowed file extensions from registered parsers."""
    from src.infrastructure.rag.steps.general.parsing.factory import get_supported_extensions

    return get_supported_extensions()


class DocumentService:
    """Service for document-related business logic."""

    def __init__(
        self,
        repository: DocumentRepository,
        blob_storage: BlobStorage,
    ):
        """
        Initialize service with repository and blob storage.

        Args:
            repository: Document repository implementation
            blob_storage: Blob storage implementation
        """
        self.repository = repository
        self.blob_storage = blob_storage

    def upload_document(
        self,
        workspace_id: int,
        filename: str,
        file_obj: BinaryIO,
        mime_type: str,
        content_hash: str,
        file_size: int,
        user_id: int,
        chunk_count: int | None = None,
        rag_collection: str | None = None,
    ) -> Document:
        """
        Upload a document to blob storage and create database record.

        Args:
            workspace_id: Workspace ID for the document
            filename: Original filename
            file_obj: File-like object to upload
            mime_type: MIME type of the file
            content_hash: SHA-256 hash of the file content
            file_size: Size of the file in bytes
            chunk_count: Optional number of chunks created by RAG
            rag_collection: Optional RAG collection name

        Returns:
            Document: Created document record

        Raises:
            DocumentProcessingError: If blob storage upload fails
        """
        try:
            # Generate blob key (using hash + original filename for uniqueness)
            blob_key = f"{content_hash}/{filename}"

            # Read file content and upload to blob storage
            file_obj.seek(0)
            file_content = file_obj.read()
            try:
                upload_url = self.blob_storage.upload(blob_key, file_content, mime_type)
            except Exception as e:
                raise DocumentProcessingError(
                    filename, f"Failed to upload to blob storage: {str(e)}"
                )

            # Create database record
            document = self.repository.create(
                workspace_id=workspace_id,
                filename=filename,
                file_path=blob_key,  # Store blob key as file_path
                file_size=file_size,
                mime_type=mime_type,
                content_hash=content_hash,
                chunk_count=0,  # Will be updated by worker
                rag_collection=rag_collection,
            )

            if not document:
                # If database creation failed, try to clean up blob storage
                from contextlib import suppress

                with suppress(Exception):
                    self.blob_storage.delete(blob_key)
                raise DocumentProcessingError(filename, "Failed to create database record")

            # Start background processing
            from src.workers import get_add_document_worker

            worker = get_add_document_worker()
            worker.start_processing(document, user_id)

            return document

        except Exception as e:
            if isinstance(e, DocumentProcessingError):
                raise
            raise DocumentProcessingError(filename, f"Upload failed: {str(e)}") from e

    def _upload_document_to_workspace_internal(
        self, workspace_id: int, user_id: int, filename: str, file_obj: BinaryIO
    ) -> DocumentUploadResult:
        """
        High-level orchestration method for document upload.

        This method handles the complete document upload workflow including
        MIME type determination, duplicate detection, text extraction, and upload.

        Args:
            workspace_id: ID of the workspace to upload to
            user_id: ID of the users uploading the document
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
            workspace_id=workspace_id,
            filename=filename,
            file_obj=file_obj,
            mime_type=mime_type,
            content_hash=content_hash,
            file_size=file_size,
            user_id=user_id,
        )

        # Document uploaded - background tasks will process it

        return DocumentUploadResult(
            document=document,
            text_length=0,  # Text length not known until processing
            is_duplicate=False,
        )

    def upload_document_to_workspace(
        self, workspace_id: int, user_id: int, filename: str, file_obj: BinaryIO
    ) -> DocumentUploadResult:
        """
        High-level orchestration method for document upload to workspace.

        This method handles the complete document upload workflow including
        MIME type determination, duplicate detection, text extraction, and upload.

        Args:
            workspace_id: ID of the workspace to upload to
            user_id: ID of the user uploading the document
            filename: Name of the file
            file_obj: File object (must support seek)

        Returns:
            DocumentUploadResult with document, text length, and duplicate flag
        """
        # Determine MIME type from filename
        extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
        mime_type = "application/pdf" if extension == "pdf" else "text/plain"

        # Get file size
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(0)  # Seek back to beginning

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
            workspace_id=workspace_id,
            filename=filename,
            file_obj=file_obj,
            mime_type=mime_type,
            content_hash=content_hash,
            file_size=file_size,
            user_id=user_id,
        )

        # Document uploaded - background tasks will process it

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
        if document:
            try:
                return self.blob_storage.download(document.file_path)
            except Exception as e:
                print(f"Error downloading document: {e}")
                return None
        return None

    def get_document_by_id(self, document_id: int) -> Document | None:
        """Get document by ID."""
        return self.repository.get_by_id(document_id)

    def get_document_by_hash(self, content_hash: str) -> Document | None:
        """Get document by content hash."""
        return self.repository.get_by_content_hash(content_hash)

    def list_user_documents(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """List all documents for a users with pagination."""
        # Note: This is a simplified implementation - in a real system,
        # we'd need to join with workspaces to filter by user access
        return (
            list(self.repository._documents.values())[skip : skip + limit]
            if hasattr(self.repository, "_documents")
            else []
        )

    def update_document(self, document_id: int, **kwargs) -> Document | None:
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
        document = None
        if delete_from_storage:
            document = self.repository.get_by_id(document_id)
            if document:
                try:
                    self.blob_storage.delete(document.file_path)
                except Exception as e:
                    print(f"Error deleting from blob storage: {e}")
                    # Continue with database deletion

        # Always attempt database deletion
        db_deleted = self.repository.delete(document_id)

        # If blob storage deletion failed but database deletion succeeded,
        # we have an orphaned file in storage - this should be handled by cleanup jobs
        if not db_deleted:
            print(f"Warning: Failed to delete document {document_id} from database")
            return False

        return True

    def calculate_file_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA-256 hash of file content."""
        file_obj.seek(0)
        hash_obj = hashlib.sha256()
        for chunk in iter(lambda: file_obj.read(4096), b""):
            hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def extract_text(self, file_obj: BinaryIO, filename: str) -> str:
        """Extract text content from file."""
        # Simple text extraction - in a real implementation this would use
        # proper parsing libraries for PDFs, DOCX, etc.
        file_obj.seek(0)
        content = file_obj.read()
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            # If not UTF-8, return a placeholder
            return f"Binary file: {filename}"

    def list_user_documents_as_dto(self, user_id: int) -> DocumentListResponse:
        """
        List all documents for a users as a DTO.

        Args:
            user_id: The users ID

        Returns:
            DocumentListResponse DTO ready for JSON serialization
        """
        documents = self.list_user_documents(user_id)
        document_dtos = DocumentMapper.documents_to_dtos(documents)

        return DocumentListResponse(
            documents=document_dtos,
            count=len(document_dtos),
            total=len(document_dtos),
        )

    def delete_document_with_validation(self, document_id: int, user_id: int) -> None:
        """
        Delete a document with validation.

        Args:
            document_id: The document ID to delete
            user_id: ID of the user performing the deletion

        Raises:
            DocumentNotFoundError: If document does not exist
        """
        # Check if document exists
        document = self.get_document_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(document_id)

        # Launch RemoveDocumentWorker in background
        from src.workers import get_remove_document_worker

        cleanup_worker = get_remove_document_worker()
        cleanup_worker.start_cleanup(document, user_id)

    def update_document_status(
        self,
        document_id: int,
        status: str,
        error_message: str | None = None,
        chunk_count: int | None = None,
    ) -> bool:
        """
        Update document processing status.

        This method is called by workers via WebSocket events to update
        document processing status as they progress through the pipeline.

        Args:
            document_id: ID of the document
            status: New processing status ('pending', 'parsing', 'chunking', 'embedding', 'indexing', 'ready', 'failed')
            error_message: Error message if status is 'failed'
            chunk_count: Number of chunks created (for indexing status)

        Returns:
            True if update was successful, False otherwise
        """
        # Validate status
        valid_statuses = [
            "pending",
            "parsing",
            "chunking",
            "embedding",
            "indexing",
            "ready",
            "failed",
        ]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        # Update document
        kwargs = {}
        kwargs["processing_status"] = status
        if error_message is not None:
            kwargs["processing_error"] = error_message
        if chunk_count is not None:
            kwargs["chunk_count"] = chunk_count

        updated_doc = self.update_document(document_id, **kwargs)

        return updated_doc is not None
