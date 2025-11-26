"""Wikipedia article fetch worker."""

import hashlib
from io import BytesIO

from flask_socketio import SocketIO

from src.domains.workspaces.documents.exceptions import DocumentProcessingError
from src.infrastructure.events import dispatch_event
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Document
from src.infrastructure.repositories.documents import DocumentRepository
from src.infrastructure.repositories.workspaces import WorkspaceRepository
from src.infrastructure.storage import BlobStorage
from src.infrastructure.wikipedia.fetch import wikipedia_fetcher
from src.workers.tasks import run_async

logger = create_logger(__name__)


class FetchWikipediaWorker:
    """
    Wikipedia article fetch worker that downloads articles and initiates document processing.

    The worker:
    1. Fetches Wikipedia article using WikipediaFetcher
    2. Saves article content to blob storage
    3. Creates document record in database
    4. Starts AddDocumentWorker for RAG processing
    5. Updates status via WebSocket
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        workspace_repository: WorkspaceRepository,
        blob_storage: BlobStorage,
        socketio: SocketIO,
    ):
        """Initialize the Wikipedia fetch worker.

        Args:
            document_repository: Document repository for database operations
            workspace_repository: Workspace repository for validation
            blob_storage: Blob storage for file operations
            socketio: Socket.IO instance for real-time updates
        """
        self.document_repository = document_repository
        self.workspace_repository = workspace_repository
        self.blob_storage = blob_storage
        self.socketio = socketio

    def start_fetch(
        self,
        workspace_id: int,
        user_id: int,
        query: str,
        language: str = "en"
    ) -> None:
        """Start Wikipedia article fetch in a background thread.

        Args:
            workspace_id: ID of the workspace to add the article to
            user_id: ID of the user performing the fetch
            query: Article title or search query
            language: Language code (default: "en")
        """
        logger.info(f"Starting Wikipedia fetch for query '{query}' in workspace {workspace_id}")

        # Execute fetch in background thread
        run_async(self._fetch_wikipedia_pipeline, workspace_id, user_id, query, language)

    def _fetch_wikipedia_pipeline(
        self,
        workspace_id: int,
        user_id: int,
        query: str,
        language: str
    ) -> None:
        """Execute the Wikipedia fetch pipeline.

        Args:
            workspace_id: ID of the workspace
            user_id: ID of the user
            query: Article title or search query
            language: Language code
        """
        try:
            # Update status to fetching
            self._update_status(
                workspace_id=workspace_id,
                user_id=user_id,
                document_id=None,  # No document yet
                status="fetching",
                message=f"Fetching Wikipedia article: {query}",
            )

            # Fetch article from Wikipedia
            logger.info(f"Fetching Wikipedia article for query: {query}")
            result = wikipedia_fetcher.fetch_article(query, language)

            if result.is_err():
                error_msg = result.err()
                logger.error(f"Wikipedia fetch failed: {error_msg}")

                self._update_status(
                    workspace_id=workspace_id,
                    user_id=user_id,
                    document_id=None,
                    status="failed",
                    message=f"Wikipedia fetch failed: {error_msg}",
                    error=error_msg,
                )
                return

            article = result.unwrap()
            logger.info(f"Successfully fetched article: {article.title}")

            # Convert article to markdown format
            content = article.to_markdown()
            content_bytes = content.encode('utf-8')
            file_size = len(content_bytes)

            # Calculate content hash
            content_hash = hashlib.sha256(content_bytes).hexdigest()

            # Check for duplicates
            existing_doc = self.document_repository.get_by_content_hash(content_hash)
            if existing_doc:
                logger.info(f"Article already exists as document {existing_doc.id}")

                self._update_status(
                    workspace_id=workspace_id,
                    user_id=user_id,
                    document_id=existing_doc.id,
                    status="ready",
                    message="Article already exists in workspace",
                )
                return

            # Create filename
            safe_title = "".join(c for c in article.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"Wikipedia - {safe_title}.md"

            # Generate blob key
            blob_key = f"{content_hash}/{filename}"

            # Upload to blob storage
            logger.info(f"Uploading article to blob storage: {blob_key}")
            file_obj = BytesIO(content_bytes)
            try:
                self.blob_storage.upload(blob_key, content_bytes, "text/markdown")
            except Exception as e:
                raise DocumentProcessingError(filename, f"Failed to upload to blob storage: {str(e)}")

            # Create document record
            logger.info(f"Creating document record for: {filename}")
            document = self.document_repository.create(
                workspace_id=workspace_id,
                filename=filename,
                file_path=blob_key,
                file_size=file_size,
                mime_type="text/markdown",
                content_hash=content_hash,
                chunk_count=0,  # Will be updated by processing worker
            )

            if not document:
                # Clean up blob storage if database creation failed
                try:
                    self.blob_storage.delete(blob_key)
                except Exception:
                    pass  # Ignore cleanup errors

                raise DocumentProcessingError(filename, "Failed to create database record")

            logger.info(f"Document created with ID: {document.id}")

            # Update status to indicate document is saved
            self._update_status(
                workspace_id=workspace_id,
                user_id=user_id,
                document_id=document.id,
                status="saved",
                message="Article saved, starting RAG processing",
            )

            # Start document processing worker
            logger.info(f"Starting RAG processing for document {document.id}")
            from src.workers import get_add_document_worker

            processing_worker = get_add_document_worker()
            processing_worker.start_processing(document, user_id)

        except Exception as e:
            logger.error(f"Wikipedia fetch pipeline failed: {e}", exc_info=True)

            self._update_status(
                workspace_id=workspace_id,
                user_id=user_id,
                document_id=None,
                status="failed",
                message=f"Wikipedia fetch failed: {str(e)}",
                error=str(e),
            )

    def _update_status(
        self,
        workspace_id: int,
        user_id: int,
        document_id: int | None,
        status: str,
        message: str,
        error: str | None = None,
    ) -> None:
        """Update fetch status and broadcast to clients.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            document_id: Document ID (if created)
            status: Fetch status
            message: Status message
            error: Error message if failed
        """
        try:
            # Broadcast via WebSocket
            status_data = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "document_id": document_id,
                "status": status,
                "message": message,
                "error": error,
            }

            dispatch_event("document.status.updated", status_data)

        except Exception as e:
            logger.error(f"Failed to update Wikipedia fetch status: {e}")


# Global worker instance (will be initialized in context)
_fetch_wikipedia_worker: FetchWikipediaWorker | None = None


def get_fetch_wikipedia_worker() -> FetchWikipediaWorker:
    """Get the global fetch Wikipedia worker instance."""
    if _fetch_wikipedia_worker is None:
        raise RuntimeError(
            "Fetch Wikipedia worker not initialized. Call initialize_fetch_wikipedia_worker() first."
        )
    return _fetch_wikipedia_worker


def initialize_fetch_wikipedia_worker(
    document_repository: DocumentRepository,
    workspace_repository: WorkspaceRepository,
    blob_storage: BlobStorage,
    socketio: SocketIO,
) -> FetchWikipediaWorker:
    """Initialize the global fetch Wikipedia worker instance.

    Args:
        document_repository: Document repository
        workspace_repository: Workspace repository
        blob_storage: Blob storage
        socketio: Socket.IO instance

    Returns:
        The initialized fetch Wikipedia worker
    """
    global _fetch_wikipedia_worker
    _fetch_wikipedia_worker = FetchWikipediaWorker(
        document_repository, workspace_repository, blob_storage, socketio
    )
    return _fetch_wikipedia_worker