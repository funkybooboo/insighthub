"""Document service implementation."""

from dataclasses import dataclass
from typing import BinaryIO, Optional

from pypdf import PdfReader
from shared.messaging import RabbitMQPublisher, publish_document_status

from .events import emit_wikipedia_fetch_status
from shared.models import Document
from shared.repositories import DocumentRepository
from shared.storage import BlobStorage
from shared.types.result import Err, Ok

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

        Raises:
            DocumentProcessingError: If blob storage upload fails
        """
        try:
            # Calculate hash and file size
            content_hash = self.calculate_file_hash(file_obj)
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()
            file_obj.seek(0)  # Reset to beginning

            # Generate blob key (using hash + original filename for uniqueness)
            blob_key = f"{content_hash}/{filename}"

            # Upload to blob storage
            upload_result = self.blob_storage.upload_file(file_obj, blob_key)
            if not upload_result.is_ok():
                raise DocumentProcessingError(
                    filename,
                    f"Failed to upload to blob storage: {upload_result.err()}"
                )

            # Create database record
            document = self.repository.create(
                user_id=user_id,
                filename=filename,
                file_path=blob_key,  # Store blob key as file_path
                file_size=file_size,
                mime_type=mime_type,
                content_hash=content_hash,
                chunk_count=chunk_count,
                rag_collection=rag_collection,
            )

            if not document:
                # If database creation failed, try to clean up blob storage
                try:
                    self.blob_storage.delete_file(blob_key)
                except Exception:
                    pass  # Ignore cleanup errors
                raise DocumentProcessingError(filename, "Failed to create database record")

            return document

        except Exception as e:
            if isinstance(e, DocumentProcessingError):
                raise
            raise DocumentProcessingError(filename, f"Upload failed: {str(e)}") from e

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

        # Publish initial status update (document uploaded, pending processing)
        workspace_id = document.workspace_id or 0
        publish_document_status(
            document_id=document.id,
            workspace_id=workspace_id,
            status="pending",
            message="Document uploaded, queued for processing",
            filename=filename,
        )

        # Publish document.uploaded event to RabbitMQ for async processing
        if self.message_publisher:
            try:
                self.message_publisher.publish(
                    routing_key="document.uploaded",
                    message={
                        "document_id": document.id,
                        "user_id": user_id,
                        "workspace_id": workspace_id,
                        "filename": filename,
                        "file_path": document.file_path,
                        "mime_type": mime_type,
                        "uploaded_at": document.created_at.isoformat(),
                    },
                )
            except Exception as e:
                # Log error but don't fail the upload - async processing can be retried
                print(f"Warning: Failed to publish document.uploaded event: {e}")

        # Document remains in "pending" status until workers process it
        # Workers will update status through the /documents/{id}/status endpoint

        return DocumentUploadResult(
            document=document,
            text_length=0,  # Text length not known until processing
            is_duplicate=False,
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
        if document:
            download_result = self.blob_storage.download_file(document.file_path)
            if download_result.is_ok():
                return download_result.unwrap()
            else:
                print(f"Error downloading document: {download_result.err()}")
                return None
        return None

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self.repository.get_by_id(document_id)

    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        return self.repository.get_by_content_hash(content_hash)

    def list_user_documents(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
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
        document = None
        if delete_from_storage:
            document = self.repository.get_by_id(document_id)
            if document:
                try:
                    delete_result = self.blob_storage.delete_file(document.file_path)
                    if not delete_result.is_ok():
                        print(f"Warning: Failed to delete from blob storage: {delete_result.err()}")
                        # Continue with database deletion even if blob storage fails
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
            total=len(document_dtos),
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

        # RAG INTEGRATION - Document Removal
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
        valid_statuses = ['pending', 'parsing', 'chunking', 'embedding', 'indexing', 'ready', 'failed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        # Update document
        update_data = {'processing_status': status}

        if error_message is not None:
            update_data['processing_error'] = error_message

        if chunk_count is not None:
            update_data['chunk_count'] = chunk_count

        updated_doc = self.update_document(document_id, **update_data)

        if updated_doc:
            # Publish status update via WebSocket
            publish_document_status(
                document_id=document_id,
                workspace_id=updated_doc.workspace_id or 0,
                status=status,
                message=f"Document {status}",
                error=error_message,
                chunk_count=chunk_count,
            )
            return True

        return False

    def upload_document_to_workspace(
        self,
        workspace_id: int,
        user_id: int,
        filename: str,
        file_obj: BinaryIO,
    ) -> DocumentUploadResponse:
        """
        Upload a document to a specific workspace.

        Args:
            workspace_id: ID of the workspace
            user_id: ID of the user uploading
            filename: Name of the file
            file_obj: File object

        Returns:
            DocumentUploadResponse DTO
        """
        # Validate filename (raises exception if invalid)
        self.validate_filename(filename)

        # Process upload
        result = self.process_document_upload(
            user_id=user_id,
            filename=filename,
            file_obj=file_obj,
        )

        # Update document with workspace_id
        updated_doc = self.update_document(result.document.id, workspace_id=workspace_id)
        if updated_doc:
            result.document.workspace_id = workspace_id

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

    def list_workspace_documents(
        self,
        workspace_id: int,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        status_filter: str | None = None,
    ) -> DocumentListResponse:
        """
        List documents in a workspace.

        Args:
            workspace_id: ID of the workspace
            user_id: ID of the user (for access control)
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            status_filter: Optional filter by processing status

        Returns:
            DocumentListResponse DTO
        """
        # Get documents by workspace
        documents = self.repository.get_by_workspace(
            workspace_id=workspace_id,
            skip=offset,
            limit=limit,
            status_filter=status_filter,
        )

        # Convert to DTOs
        document_dtos = DocumentMapper.documents_to_dtos(documents)

        return DocumentListResponse(
            documents=document_dtos,
            count=len(document_dtos),
            total=self.repository.count_by_workspace(workspace_id, status_filter),
        )

    def delete_workspace_document(
        self,
        document_id: int,
        workspace_id: int,
        user_id: int,
    ) -> None:
        """
        Delete a document from a workspace.

        Args:
            document_id: ID of the document
            workspace_id: ID of the workspace
            user_id: ID of the user (for access control)

        Raises:
            DocumentNotFoundError: If document doesn't exist or not in workspace
        """
        # Get document and verify it belongs to the workspace
        document = self.get_document_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(document_id)

        if document.workspace_id != workspace_id:
            raise DocumentNotFoundError(document_id)

        # Publish document.deleted event to RabbitMQ
        if self.message_publisher:
            try:
                self.message_publisher.publish(
                    routing_key="document.deleted",
                    message={
                        "document_id": document_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "file_path": document.file_path,
                        "filename": document.filename,
                    },
                )
            except Exception as e:
                print(f"Warning: Failed to publish document.deleted event: {e}")

        # Delete document
        self.delete_document_with_validation(document_id)

    def fetch_wikipedia_article(
        self,
        workspace_id: int,
        user_id: int,
        query: str,
        language: str = "en",
    ) -> DocumentUploadResponse:
        """
        Initiate Wikipedia article fetch for a workspace.

        This method creates a placeholder document and publishes an event
        for async processing by the Wikipedia worker.

        Args:
            workspace_id: ID of the workspace
            user_id: ID of the user
            query: Search query for the article
            language: Language code (default: "en")

        Returns:
            DocumentUploadResponse DTO with placeholder document
        """
        from io import BytesIO

        # Create a placeholder document initially
        filename = f"Wikipedia_{query.replace(' ', '_')}_pending.md"
        placeholder_content = f"# Wikipedia Article: {query}\n\n*Fetching content from Wikipedia...*\n\n---\n*Language: {language}*"

        # Create file-like object with placeholder content
        file_obj = BytesIO(placeholder_content.encode('utf-8'))

        # Upload placeholder document
        result = self.upload_document_to_workspace(
            workspace_id=workspace_id,
            user_id=user_id,
            filename=filename,
            file_obj=file_obj,
        )

        # Publish wikipedia.fetch_requested event for async processing
        if self.message_publisher:
            try:
                self.message_publisher.publish(
                    routing_key="wikipedia.fetch_requested",
                    message={
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "query": query,
                        "language": language,
                        "document_id": result.document.id,
                        "requested_at": result.document.created_at.isoformat(),
                    },
                )

                # Emit initial status update
                emit_wikipedia_fetch_status(
                    workspace_id=workspace_id,
                    query=query,
                    status="fetching",
                    message="Initiating Wikipedia article fetch"
                )

            except Exception as e:
                print(f"Warning: Failed to publish wikipedia.fetch_requested event: {e}")
                # Update document status to failed
                self.update_document_status(
                    document_id=result.document.id,
                    status="failed",
                    error_message=f"Failed to initiate fetch: {str(e)}"
                )
                raise DocumentProcessingError(query, f"Failed to initiate Wikipedia fetch: {str(e)}")

        return result
