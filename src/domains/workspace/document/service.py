"""Document service implementation."""

from io import BytesIO

from src.config import config
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Document, Workspace
from src.infrastructure.rag.steps.general.parsing.utils import (
    calculate_file_hash,
    determine_mime_type,
)
from src.infrastructure.rag.workflows.add_document import AddDocumentWorkflowFactory
from src.infrastructure.rag.workflows.remove_document import RemoveDocumentWorkflowFactory
from src.infrastructure.repositories import DocumentRepository, WorkspaceRepository
from src.infrastructure.storage import BlobStorage

logger = create_logger(__name__)


class DocumentService:
    """Service for document-related business logic."""

    def __init__(
        self,
        repository: DocumentRepository,
        workspace_repository: WorkspaceRepository,
        blob_storage: BlobStorage,
    ):
        """Initialize service with repositories and storage.

        Args:
            repository: Document repository implementation
            workspace_repository: Workspace repository implementation
            blob_storage: Blob storage implementation
        """
        self.repository = repository
        self.workspace_repository = workspace_repository
        self.blob_storage = blob_storage

    def upload_and_process_document(
        self,
        workspace_id: int,
        filename: str,
        file_content: bytes,
    ) -> Document:
        """Upload and process a document synchronously (CLI system).

        Args:
            workspace_id: Workspace ID for the document
            filename: Original filename
            file_content: File content as bytes

        Returns:
            Document: Created document record with status 'ready' or 'failed'

        Raises:
            ValueError: If workspace not found or processing fails
        """
        logger.info(f"Uploading document: filename='{filename}', workspace_id={workspace_id}")

        # Get workspace
        workspace = self.workspace_repository.get_by_id(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        # Calculate hash and determine MIME type
        file_obj = BytesIO(file_content)
        content_hash = calculate_file_hash(file_obj)
        mime_type = determine_mime_type(filename)

        # Upload to blob storage
        blob_key = f"{content_hash}/{filename}"
        try:
            self.blob_storage.upload(blob_key, file_content, mime_type)
            logger.info(f"Document uploaded to blob storage: blob_key='{blob_key}'")
        except Exception as e:
            logger.error(f"Blob storage upload failed: {e}")
            raise ValueError(f"Failed to upload to blob storage: {e}")

        # Create database record
        document = self.repository.create(
            workspace_id=workspace_id,
            filename=filename,
            file_path=blob_key,
            file_size=len(file_content),
            mime_type=mime_type,
            content_hash=content_hash,
            chunk_count=0,
            status="processing",
        )

        if not document:
            # Clean up blob storage
            try:
                self.blob_storage.delete(blob_key)
            except Exception:
                pass
            raise ValueError("Failed to create database record")

        logger.info(f"Document record created: document_id={document.id}")

        # Process document through RAG workflow
        try:
            self._process_document(workspace, document, file_content)
            # Update status to ready
            self.repository.update(document.id, status="ready")
            logger.info(f"Document processed successfully: document_id={document.id}")
        except Exception as e:
            # Update status to failed
            self.repository.update(document.id, status="failed")
            logger.error(f"Document processing failed: {e}", exc_info=True)
            raise ValueError(f"Failed to process document: {e}")

        # Reload document with updated status
        document = self.repository.get_by_id(document.id)
        if not document:
            raise ValueError("Failed to reload document after processing")

        return document

    def _process_document(
        self,
        workspace: Workspace,
        document: Document,
        file_content: bytes,
    ) -> None:
        """Process document through RAG workflow.

        Args:
            workspace: Workspace the document belongs to
            document: Document record
            file_content: File content as bytes

        Raises:
            Exception: If processing fails
        """
        logger.info(f"Processing document {document.id} through RAG workflow")

        # Build RAG configuration
        rag_config = self._build_rag_config(workspace)

        # Create and execute workflow
        workflow = AddDocumentWorkflowFactory.create(rag_config)
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

        if result.is_err():
            error = result.err()
            raise Exception(f"Workflow execution failed: {error.message}")

        chunks_indexed = result.ok()
        logger.info(f"Document processed: {chunks_indexed} chunks indexed")

        # Update chunk count
        self.repository.update(document.id, chunk_count=chunks_indexed)

    def _build_rag_config(self, workspace: Workspace) -> dict:
        """Build RAG configuration from workspace."""
        return {
            "rag_type": workspace.rag_type,
            "parser_type": "text",  # Auto-detect based on file type
            "chunker_type": "sentence",
            "chunker_config": {
                "chunk_size": 500,
                "overlap": 50,
            },
            "embedder_type": "nomic-embed-text",  # Model name is the embedder type
            "embedder_config": {
                "base_url": config.llm.ollama_base_url,
            },
            "vector_store_type": "qdrant",
            "vector_store_config": {
                "host": config.vector_store.qdrant_host,
                "port": config.vector_store.qdrant_port,
                "collection_name": f"workspace_{workspace.id}",
            },
            "enable_reranking": False,
        }

    def remove_document(self, document_id: int) -> bool:
        """Remove document and its RAG data.

        Args:
            document_id: Document ID to remove

        Returns:
            bool: True if deleted, False if not found
        """
        logger.info(f"Removing document: document_id={document_id}")

        # Get document
        document = self.repository.get_by_id(document_id)
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
            try:
                self.blob_storage.delete(document.file_path)
                logger.info(f"Document deleted from blob storage: {document.file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete from blob storage: {e}")

        # Delete from database
        deleted = self.repository.delete(document_id)
        if deleted:
            logger.info(f"Document deleted: document_id={document_id}")
        else:
            logger.error(f"Failed to delete document: document_id={document_id}")

        return deleted

    def _remove_from_rag_index(self, workspace: Workspace, document: Document) -> None:
        """Remove document from RAG index.

        Args:
            workspace: Workspace the document belongs to
            document: Document to remove

        Raises:
            Exception: If removal fails
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

        if result.is_err():
            error = result.err()
            raise Exception(f"Removal workflow failed: {error.message}")

        logger.info(f"Document removed from RAG index: document_id={document.id}")

    def list_documents_by_workspace(self, workspace_id: int) -> list[Document]:
        """List all documents for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            list[Document]: List of documents
        """
        return self.repository.get_by_workspace(workspace_id)

    def get_document_by_id(self, document_id: int) -> Document | None:
        """Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Optional[Document]: Document if found, None otherwise
        """
        return self.repository.get_by_id(document_id)
