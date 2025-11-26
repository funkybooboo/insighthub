"""Add document worker that executes add document workflows."""

from io import BytesIO

from flask_socketio import SocketIO

from src.infrastructure.events import dispatch_event
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Document
from src.infrastructure.rag.workflows.factory import WorkflowFactory
from src.infrastructure.repositories.documents import DocumentRepository
from src.infrastructure.repositories.workspaces import WorkspaceRepository
from src.infrastructure.storage import BlobStorage
from src.workers.tasks import run_async

logger = create_logger(__name__)


class AddDocumentWorker:
    """
    Document processing worker that executes add document workflows in background threads.

    The worker:
    1. Receives document processing requests
    2. Looks up workspace RAG configuration
    3. Dynamically creates appropriate workflow using WorkflowFactory
    4. Downloads document content from blob storage
    5. Executes the workflow (Vector RAG, Graph RAG, etc.)
    6. Updates status in database and broadcasts via WebSocket
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        workspace_repository: WorkspaceRepository,
        blob_storage: BlobStorage,
        socketio: SocketIO,
    ):
        """Initialize the add document worker.

        Args:
            document_repository: Document repository for database operations
            workspace_repository: Workspace repository for RAG config lookup
            blob_storage: Blob storage for file operations
            socketio: Socket.IO instance for real-time updates
        """
        self.document_repository = document_repository
        self.workspace_repository = workspace_repository
        self.blob_storage = blob_storage
        self.socketio = socketio

    def start_processing(self, document: Document, user_id: int) -> None:
        """Start document processing in a background thread.

        Args:
            document: The document to process
            user_id: ID of the user who uploaded the document
        """
        logger.info(f"Starting background processing for document {document.id}")

        # Execute workflow in background thread
        run_async(self._process_document_pipeline, document, user_id)

    def _process_document_pipeline(self, document: Document, user_id: int) -> None:
        """Execute the add document workflow pipeline.

        Args:
            document: The document to process
            user_id: ID of the user who uploaded the document
        """
        try:
            # Update status to processing
            self._update_status(
                document.id,
                user_id,
                document.workspace_id,
                "processing",
                "Starting document processing",
            )

            # Get workspace RAG configuration
            logger.info(f"Looking up workspace {document.workspace_id} RAG config")
            workspace = self.workspace_repository.get_by_id(document.workspace_id)
            if not workspace:
                raise Exception(f"Workspace {document.workspace_id} not found")

            rag_config = self._build_rag_config(workspace)
            logger.info(f"Using RAG type: {rag_config.get('rag_type')}")

            # Create workflow dynamically based on workspace RAG config
            add_document_workflow = WorkflowFactory.create_add_document_workflow(rag_config)

            # Download document from blob storage
            logger.info(f"Downloading document {document.id} from blob storage")
            if not document.file_path:
                raise Exception(f"Document {document.id} has no file_path")
            try:
                file_content = self.blob_storage.download(document.file_path)
            except Exception as e:
                raise Exception(f"Failed to download document: {e}") from e

            # Execute the add document workflow
            logger.info(f"Executing add document workflow for document {document.id}")
            result = add_document_workflow.execute(
                raw_document=BytesIO(file_content),
                document_id=str(document.id),
                workspace_id=str(document.workspace_id),
                metadata={
                    "filename": document.filename,
                    "mime_type": document.mime_type,
                    "file_size": str(document.file_size),
                },
            )

            # Handle result
            if result.is_ok():
                chunk_count = result.unwrap()
                logger.info(
                    f"Document {document.id} processed successfully: {chunk_count} chunks indexed"
                )

                # Update status to ready
                self._update_status(
                    document.id,
                    user_id,
                    document.workspace_id,
                    "ready",
                    f"Document processed: {chunk_count} chunks indexed",
                    chunk_count=chunk_count,
                )

            else:
                # Workflow returned an error
                error = result.err()
                logger.error(f"Workflow failed for document {document.id}: {error}")

                self._update_status(
                    document.id,
                    user_id,
                    document.workspace_id,
                    "failed",
                    f"Processing failed: {error.message}",
                    error=str(error),
                )

        except Exception as e:
            logger.error(f"Document {document.id} processing failed: {e}", exc_info=True)

            # Update status to failed
            self._update_status(
                document.id,
                user_id,
                document.workspace_id,
                "failed",
                f"Processing failed: {str(e)}",
                error=str(e),
            )

            # Clean up any partial data
            self._cleanup_failed_processing(document)

    def _build_rag_config(self, workspace: object) -> dict:
        """Build RAG configuration dictionary from workspace model.

        Args:
            workspace: Workspace model with RAG configuration

        Returns:
            RAG configuration dictionary for WorkflowFactory
        """
        # Extract RAG config from workspace model
        # Default to vector RAG if not specified
        return {
            "rag_type": getattr(workspace, "rag_type", "vector"),
            "parser_type": getattr(workspace, "parser_type", "text"),
            "chunker_type": getattr(workspace, "chunker_type", "sentence"),
            "chunker_config": getattr(workspace, "chunker_config", {"chunk_size": 500, "overlap": 50}),
            "embedder_type": getattr(workspace, "embedder_type", "ollama"),
            "embedder_config": getattr(workspace, "embedder_config", {
                "base_url": "http://localhost:11434",
                "model_name": "nomic-embed-text",
            }),
            "vector_store_type": getattr(workspace, "vector_store_type", "qdrant"),
            "vector_store_config": getattr(workspace, "vector_store_config", {
                "host": "localhost",
                "port": 6333,
                "collection_name": f"workspace_{workspace.id}",
            }),
            "enable_reranking": getattr(workspace, "enable_reranking", False),
        }

    def _update_status(
        self,
        document_id: int,
        user_id: int,
        workspace_id: int | None,
        status: str,
        message: str,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> None:
        """Update document processing status and dispatch event.

        Args:
            document_id: Document ID
            user_id: User ID
            workspace_id: Workspace ID
            status: Processing status
            message: Status message
            error: Error message if failed
            chunk_count: Number of chunks created
        """
        try:
            # Update in database
            self.document_repository.update(document_id, processing_status=status)
            if error:
                self.document_repository.update(document_id, processing_error=error)
            if chunk_count is not None:
                self.document_repository.update(document_id, chunk_count=chunk_count)

            # Dispatch document status update event
            event_data = {
                "document_id": document_id,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "status": status,
                "message": message,
                "filename": "",  # Could be populated from document
                "error": error,
                "chunk_count": chunk_count,
            }

            dispatch_event("document.status.updated", event_data)

        except Exception as e:
            logger.error(f"Failed to update document status: {e}")

    def _cleanup_failed_processing(self, document: Document) -> None:
        """Clean up any partial processing data for failed documents.

        Args:
            document: The document that failed processing
        """
        try:
            # Could clean up partial vector store data, etc.
            logger.info(f"Cleaning up failed processing for document {document.id}")

            # TODO: Clean up indexed chunks from vector store if needed
            # workflow.cleanup(document_id=str(document.id))

        except Exception as e:
            logger.warning(f"Failed to cleanup document {document.id}: {e}")


# Global worker instance (will be initialized in context)
_add_document_worker: AddDocumentWorker | None = None


def get_add_document_worker() -> AddDocumentWorker:
    """Get the global add document worker instance."""
    if _add_document_worker is None:
        raise RuntimeError(
            "Add document worker not initialized. Call initialize_add_document_worker() first."
        )
    return _add_document_worker


def initialize_add_document_worker(
    document_repository: DocumentRepository,
    workspace_repository: WorkspaceRepository,
    blob_storage: BlobStorage,
    socketio: SocketIO,
) -> AddDocumentWorker:
    """Initialize the global add document worker instance.

    Args:
        document_repository: Document repository
        workspace_repository: Workspace repository for RAG config lookup
        blob_storage: Blob storage
        socketio: Socket.IO instance

    Returns:
        The initialized add document worker
    """
    global _add_document_worker
    _add_document_worker = AddDocumentWorker(
        document_repository, workspace_repository, blob_storage, socketio
    )
    return _add_document_worker
