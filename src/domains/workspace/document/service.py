"""Document service implementation."""

from io import BytesIO
from typing import Any, Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.document.data_access import DocumentDataAccess
from src.domains.workspace.document.models import Document, DocumentStatus
from src.domains.workspace.models import Workspace
from src.domains.workspace.rag_config_provider import RagConfigProviderFactory
from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.general.parsing.utils import (
    calculate_file_hash,
    determine_mime_type,
)
from src.infrastructure.rag.workflows.add_document import AddDocumentWorkflowFactory
from src.infrastructure.rag.workflows.remove_document import RemoveDocumentWorkflowFactory
from src.infrastructure.storage import BlobStorage
from src.infrastructure.types import DatabaseError, NotFoundError, StorageError, WorkflowError

logger = create_logger(__name__)


class DocumentService:
    """Service for document-related business logic."""

    def __init__(
        self,
        data_access: DocumentDataAccess,
        workspace_repository: WorkspaceRepository,
        blob_storage: BlobStorage,
        config_provider_factory: RagConfigProviderFactory,
    ):
        """Initialize service with data access, workspace repository, and storage.

        Args:
            data_access: Document data access layer (handles cache + repository)
            workspace_repository: Workspace repository (needed for RAG config)
            blob_storage: Blob storage implementation (needed for file operations)
            config_provider_factory: Factory for RAG config providers
        """
        self.data_access = data_access
        self.workspace_repository = workspace_repository
        self.blob_storage = blob_storage
        self.config_provider_factory = config_provider_factory

    def upload_and_process_document(
        self,
        workspace_id: int,
        filename: str,
        file_content: bytes,
    ) -> Result[Document, NotFoundError | StorageError | WorkflowError | DatabaseError]:
        """Upload and process a document synchronously (CLI system).

        Args:
            workspace_id: Workspace ID for the document
            filename: Original filename
            file_content: File content as bytes

        Returns:
            Result containing Document with status 'ready' or 'failed', or error
        """
        logger.info(f"Uploading document: filename='{filename}', workspace_id={workspace_id}")

        # Get workspace
        workspace = self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            return Failure(NotFoundError("workspace", workspace_id))

        # Calculate hash and determine MIME type
        file_obj = BytesIO(file_content)
        content_hash = calculate_file_hash(file_obj)
        mime_type = determine_mime_type(filename)

        # Upload to blob storage
        blob_key = f"{content_hash}/{filename}"
        logger.info(f"Uploading document to blob storage: blob_key='{blob_key}'")
        upload_result = self.blob_storage.upload(blob_key, file_content, mime_type)
        if isinstance(upload_result, Failure):
            logger.error(f"Blob storage upload failed: {upload_result.failure().message}")
            return upload_result

        logger.info(f"Document uploaded to blob storage: blob_key='{blob_key}'")

        # Create database record via data access layer
        create_result = self.data_access.create(
            workspace_id=workspace_id,
            filename=filename,
            file_path=blob_key,
            file_size=len(file_content),
            mime_type=mime_type,
            content_hash=content_hash,
            chunk_count=0,
            status=DocumentStatus.UPLOADED.value,
        )

        if isinstance(create_result, Failure):
            # Clean up blob storage
            self.blob_storage.delete(blob_key)
            return create_result

        document = create_result.unwrap()

        logger.info(f"Document record created: document_id={document.id}")

        # Process document through RAG workflow
        process_result = self._process_document(workspace, document, file_content)
        if isinstance(process_result, Failure):
            # Update status to failed
            self.data_access.update(document.id, status=DocumentStatus.FAILED.value)
            logger.error(f"Document processing failed: {process_result.failure().message}")
            return Failure(process_result.failure())

        # Update status to ready
        self.data_access.update(document.id, status=DocumentStatus.READY.value)
        logger.info(f"Document processed successfully: document_id={document.id}")

        # Reload document with updated status (data_access handles caching)
        reloaded_document = self.data_access.get_by_id(document.id)
        if not reloaded_document:
            return Failure(NotFoundError("document", document.id))

        return Success(reloaded_document)

    def _process_document(
        self,
        workspace: Workspace,
        document: Document,
        file_content: bytes,
    ) -> Result[int, WorkflowError]:
        """Process document through RAG workflow with status tracking.

        Args:
            workspace: Workspace the document belongs to
            document: Document record
            file_content: File content as bytes

        Returns:
            Result containing number of chunks indexed, or error
        """
        logger.info(f"Processing document {document.id} through RAG workflow")

        # Build RAG configuration
        rag_config = self._build_rag_config(workspace)

        # Update status: parsing
        self.data_access.update(document.id, status=DocumentStatus.PARSING.value)
        logger.info(f"Document {document.id}: parsing stage")

        # Create and execute workflow
        # Note: The workflow internally does: parse -> chunk -> embed -> index
        # We update status at key milestones
        workflow = AddDocumentWorkflowFactory.create(rag_config)

        # Execute workflow - this does all the heavy lifting
        result = workflow.execute(
            raw_document=BytesIO(file_content),
            document_id=str(document.id),
            workspace_id=str(workspace.id),
            metadata={
                "filename": document.filename,
                "mime_type": document.mime_type,
                "file_size": str(document.file_size),
            },
        )

        if isinstance(result, Failure):
            error = result.failure()
            return Failure(
                WorkflowError(
                    f"Workflow execution failed: {error.message}", workflow="process_document"
                )
            )

        chunks_indexed = result.unwrap()

        # Update status: indexing complete (workflow finished successfully)
        self.data_access.update(document.id, status=DocumentStatus.INDEXED.value)
        logger.info(f"Document {document.id}: {chunks_indexed} chunks indexed")

        # Update chunk count
        self.data_access.update(document.id, chunk_count=chunks_indexed)

        return Success(chunks_indexed)

    def _build_rag_config(self, workspace: Workspace) -> dict[str, Any]:
        """Build RAG configuration from workspace's stored configuration."""
        # Use provider pattern to build indexing configuration
        provider = self.config_provider_factory.get_provider(workspace.rag_type)
        if not provider:
            logger.warning(f"Unknown RAG type: {workspace.rag_type}")
            return {"rag_type": workspace.rag_type, "parser_type": "text"}

        return provider.build_indexing_settings(workspace.id)

    def remove_document(self, document_id: int) -> bool:
        """Remove document and its RAG data.

        Args:
            document_id: Document ID to remove

        Returns:
            bool: True if deleted, False if not found
        """
        logger.info(f"Removing document: document_id={document_id}")

        # Get document
        document = self.data_access.get_by_id(document_id)
        if not document:
            logger.warning(f"Document not found: document_id={document_id}")
            return False

        # Get workspace for RAG config
        workspace = self.workspace_repository.get_by_id(document.workspace_id)
        if workspace:
            # Remove from RAG index
            try:
                self._remove_from_rag_index(workspace, document)
            except Exception as e:
                logger.warning(f"Failed to remove from RAG index: {e}")

        # Delete from blob storage
        if document.file_path:
            deleted = self.blob_storage.delete(document.file_path)
            if deleted:
                logger.info(f"Document deleted from blob storage: {document.file_path}")
            else:
                logger.warning(f"Failed to delete from blob storage: {document.file_path}")

        # Delete from database (data_access handles cache invalidation)
        return self.data_access.delete(document_id)

    def _remove_from_rag_index(
        self, workspace: Workspace, document: Document
    ) -> Result[None, WorkflowError]:
        """Remove document from RAG index.

        Args:
            workspace: Workspace the document belongs to
            document: Document to remove

        Returns:
            Result containing None on success, or error
        """
        logger.info(f"Removing document {document.id} from RAG index")

        # Build RAG configuration
        rag_config = self._build_rag_config(workspace)

        # Create and execute removal workflow
        workflow = RemoveDocumentWorkflowFactory.create(rag_config)
        result = workflow.execute(
            document_id=str(document.id),
            workspace_id=str(workspace.id),
        )

        if isinstance(result, Failure):
            error = result.failure()
            return Failure(
                WorkflowError(
                    f"Removal workflow failed: {error.message}", workflow="remove_document_from_rag"
                )
            )

        logger.info(f"Document removed from RAG index: document_id={document.id}")
        return Success(None)

    def list_documents_by_workspace(self, workspace_id: int) -> list[Document]:
        """List all documents for a workspace with caching (handled by data access layer).

        Args:
            workspace_id: Workspace ID

        Returns:
            list[Document]: List of documents
        """
        return self.data_access.get_by_workspace(workspace_id)

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID with caching (handled by data access layer).

        Args:
            document_id: Document ID

        Returns:
            Optional[Document]: Document if found, None otherwise
        """
        return self.data_access.get_by_id(document_id)
