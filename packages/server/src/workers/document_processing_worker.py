"""Document processing worker that executes consume workflows."""

from io import BytesIO

from flask_socketio import SocketIO

from src.infrastructure.events import broadcast_document_status
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Document
from src.infrastructure.rag.workflows import ConsumeWorkflow
from src.infrastructure.repositories.documents import DocumentRepository
from src.infrastructure.storage import BlobStorage
from src.workers.tasks import run_async

logger = create_logger(__name__)


class DocumentProcessor:
    """
    Document processing worker that executes consume workflows in background threads.

    The processor:
    1. Receives document processing requests
    2. Downloads document content from blob storage
    3. Executes the appropriate consume workflow (Vector RAG, Graph RAG, etc.)
    4. Updates status in database and broadcasts via WebSocket
    """

    def __init__(
        self,
        repository: DocumentRepository,
        blob_storage: BlobStorage,
        socketio: SocketIO,
        consume_workflow: ConsumeWorkflow,
    ):
        """Initialize the document processor.

        Args:
            repository: Document repository for database operations
            blob_storage: Blob storage for file operations
            socketio: Socket.IO instance for real-time updates
            consume_workflow: Workflow implementation to execute (injected)
        """
        self.repository = repository
        self.blob_storage = blob_storage
        self.socketio = socketio
        self.consume_workflow = consume_workflow

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
        """Execute the consume workflow pipeline.

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

            # Download document from blob storage
            logger.info(f"Downloading document {document.id} from blob storage")
            try:
                file_content = self.blob_storage.download(document.file_path)
            except Exception as e:
                raise Exception(f"Failed to download document: {e}") from e

            # Execute the consume workflow
            logger.info(
                f"Executing consume workflow for document {document.id}"
            )
            result = self.consume_workflow.execute(
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
        """Update document processing status and broadcast to clients.

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
            self.repository.update(document_id, processing_status=status)
            if error:
                self.repository.update(document_id, processing_error=error)
            if chunk_count is not None:
                self.repository.update(document_id, chunk_count=chunk_count)

            # Broadcast via WebSocket
            status_data = {
                "document_id": document_id,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "status": status,
                "message": message,
                "filename": "",  # Could be populated from document
                "error": error,
                "chunk_count": chunk_count,
            }

            broadcast_document_status(status_data, self.socketio)

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


# Global processor instance (will be initialized in context)
_document_processor: DocumentProcessor | None = None


def get_document_processor() -> DocumentProcessor:
    """Get the global document processor instance."""
    if _document_processor is None:
        raise RuntimeError(
            "Document processor not initialized. Call initialize_document_processor() first."
        )
    return _document_processor


def initialize_document_processor(
    repository: DocumentRepository,
    blob_storage: BlobStorage,
    socketio: SocketIO,
    consume_workflow: ConsumeWorkflow,
) -> DocumentProcessor:
    """Initialize the global document processor instance.

    Args:
        repository: Document repository
        blob_storage: Blob storage
        socketio: Socket.IO instance
        consume_workflow: Consume workflow implementation (Vector RAG, Graph RAG, etc.)

    Returns:
        The initialized document processor
    """
    global _document_processor
    _document_processor = DocumentProcessor(
        repository, blob_storage, socketio, consume_workflow
    )
    return _document_processor
