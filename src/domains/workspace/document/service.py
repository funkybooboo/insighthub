"""Document service implementation."""

import json
from io import BytesIO
from typing import Optional

from returns.result import Failure, Result, Success

from src.config import config
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Document, Workspace
from src.infrastructure.rag.options import (
    get_default_chunking_algorithm,
    get_default_embedding_algorithm,
)
from src.infrastructure.rag.steps.general.parsing.utils import (
    calculate_file_hash,
    determine_mime_type,
)
from src.infrastructure.rag.workflows.add_document import AddDocumentWorkflowFactory
from src.infrastructure.rag.workflows.remove_document import RemoveDocumentWorkflowFactory
from src.infrastructure.repositories import DocumentRepository, WorkspaceRepository
from src.infrastructure.storage import BlobStorage
from src.infrastructure.types import DatabaseError, NotFoundError, StorageError, WorkflowError

logger = create_logger(__name__)


class DocumentService:
    """Service for document-related business logic."""

    def __init__(
        self,
        repository: DocumentRepository,
        workspace_repository: WorkspaceRepository,
        blob_storage: BlobStorage,
        cache: Optional[Cache] = None,
    ):
        """Initialize service with repositories and storage.

        Args:
            repository: Document repository implementation
            workspace_repository: Workspace repository implementation
            blob_storage: Blob storage implementation
            cache: Optional cache implementation
        """
        self.repository = repository
        self.workspace_repository = workspace_repository
        self.blob_storage = blob_storage
        self.cache = cache

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
        try:
            self.blob_storage.upload(blob_key, file_content, mime_type)
            logger.info(f"Document uploaded to blob storage: blob_key='{blob_key}'")
        except Exception as e:
            logger.error(f"Blob storage upload failed: {e}")
            return Failure(StorageError(str(e), operation="upload"))

        # Create database record
        create_result = self.repository.create(
            workspace_id=workspace_id,
            filename=filename,
            file_path=blob_key,
            file_size=len(file_content),
            mime_type=mime_type,
            content_hash=content_hash,
            chunk_count=0,
            status="processing",
        )

        if isinstance(create_result, Failure):
            # Clean up blob storage
            try:
                self.blob_storage.delete(blob_key)
            except Exception:
                pass
            return Failure(create_result.failure())

        document = create_result.unwrap()
        logger.info(f"Document record created: document_id={document.id}")

        # Process document through RAG workflow
        process_result = self._process_document(workspace, document, file_content)
        if isinstance(process_result, Failure):
            # Update status to failed
            self.repository.update(document.id, status="failed")
            logger.error(f"Document processing failed: {process_result.failure().message}")
            return Failure(process_result.failure())

        # Update status to ready
        self.repository.update(document.id, status="ready")
        logger.info(f"Document processed successfully: document_id={document.id}")

        # Reload document with updated status
        reloaded_document = self.repository.get_by_id(document.id)
        if not reloaded_document:
            return Failure(NotFoundError("document", document.id))

        # Cache the document
        if self.cache:
            self._cache_document(reloaded_document)
            # Invalidate workspace documents list cache
            self._invalidate_workspace_documents_cache(workspace_id)

        return Success(reloaded_document)

    def _process_document(
        self,
        workspace: Workspace,
        document: Document,
        file_content: bytes,
    ) -> Result[int, WorkflowError]:
        """Process document through RAG workflow.

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

        if isinstance(result, Failure):
            error = result.failure()
            return Failure(
                WorkflowError(
                    f"Workflow execution failed: {error.message}", workflow="process_document"
                )
            )

        chunks_indexed = result.unwrap()
        logger.info(f"Document processed: {chunks_indexed} chunks indexed")

        # Update chunk count
        self.repository.update(document.id, chunk_count=chunks_indexed)

        return Success(chunks_indexed)

    def _build_rag_config(self, workspace: Workspace) -> dict:
        """Build RAG configuration from workspace's stored configuration."""
        base_config = {
            "rag_type": workspace.rag_type,
            "parser_type": "text",  # Auto-detect based on file type
        }

        if workspace.rag_type == "vector":
            # Get workspace-specific vector RAG config
            vector_config = self.workspace_repository.get_vector_rag_config(workspace.id)

            if vector_config:
                base_config.update({
                    "chunker_type": vector_config.chunking_algorithm,
                    "chunker_config": {
                        "chunk_size": vector_config.chunk_size,
                        "overlap": vector_config.chunk_overlap,
                    },
                    "embedder_type": vector_config.embedding_algorithm,
                    "embedder_config": {
                        "base_url": config.llm.ollama_base_url,
                    },
                    "vector_store_type": "qdrant",
                    "vector_store_config": {
                        "host": config.vector_store.qdrant_host,
                        "port": config.vector_store.qdrant_port,
                        "collection_name": f"workspace_{workspace.id}",
                    },
                    "enable_reranking": vector_config.rerank_algorithm != "none",
                    "reranker_type": vector_config.rerank_algorithm,
                })
            else:
                # Fallback to defaults if no config found
                base_config.update({
                    "chunker_type": get_default_chunking_algorithm(),
                    "chunker_config": {
                        "chunk_size": 500,
                        "overlap": 50,
                    },
                    "embedder_type": get_default_embedding_algorithm(),
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
                })
        elif workspace.rag_type == "graph":
            # Get workspace-specific graph RAG config
            graph_config = self.workspace_repository.get_graph_rag_config(workspace.id)

            if graph_config:
                base_config.update({
                    "entity_extraction_algorithm": graph_config.entity_extraction_algorithm,
                    "relationship_extraction_algorithm": graph_config.relationship_extraction_algorithm,
                    "clustering_algorithm": graph_config.clustering_algorithm,
                })
            # Note: Graph RAG workflow not fully implemented yet

        return base_config

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
            # Invalidate cache
            if self.cache:
                self._invalidate_document_cache(document_id)
                self._invalidate_workspace_documents_cache(document.workspace_id)
        else:
            logger.error(f"Failed to delete document: document_id={document_id}")

        return deleted

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
        """List all documents for a workspace with caching.

        Args:
            workspace_id: Workspace ID

        Returns:
            list[Document]: List of documents
        """
        # Try cache first
        if self.cache:
            cached = self._get_cached_workspace_documents(workspace_id)
            if cached is not None:
                logger.debug(f"Cache hit for workspace {workspace_id} documents")
                return cached

        # Cache miss, fetch from database
        documents = self.repository.get_by_workspace(workspace_id)

        # Cache the result
        if self.cache:
            self._cache_workspace_documents(workspace_id, documents)
            # Also cache individual documents
            for doc in documents:
                self._cache_document(doc)

        return documents

    def get_document_by_id(self, document_id: int) -> Document | None:
        """Get document by ID with caching.

        Args:
            document_id: Document ID

        Returns:
            Optional[Document]: Document if found, None otherwise
        """
        # Try cache first
        if self.cache:
            cached = self._get_cached_document(document_id)
            if cached:
                logger.debug(f"Cache hit for document {document_id}")
                return cached

        # Cache miss, fetch from database
        document = self.repository.get_by_id(document_id)
        if document and self.cache:
            self._cache_document(document)

        return document

    def _cache_document(self, document: Document) -> None:
        """Cache a document object."""
        if not self.cache:
            return
        key = f"document:{document.id}"
        value = json.dumps({
            "id": document.id,
            "workspace_id": document.workspace_id,
            "filename": document.filename,
            "file_path": document.file_path,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
            "content_hash": document.content_hash,
            "chunk_count": document.chunk_count,
            "status": document.status,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
        })
        self.cache.set(key, value, ttl=300)  # Cache for 5 minutes

    def _get_cached_document(self, document_id: int) -> Document | None:
        """Get document from cache."""
        if not self.cache:
            return None
        key = f"document:{document_id}"
        cached = self.cache.get(key)
        if not cached:
            return None
        try:
            from datetime import datetime
            data = json.loads(cached)
            return Document(
                id=data["id"],
                workspace_id=data["workspace_id"],
                filename=data["filename"],
                file_path=data["file_path"],
                file_size=data["file_size"],
                mime_type=data["mime_type"],
                content_hash=data["content_hash"],
                chunk_count=data["chunk_count"],
                status=data["status"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _invalidate_document_cache(self, document_id: int) -> None:
        """Invalidate document cache."""
        if not self.cache:
            return
        key = f"document:{document_id}"
        self.cache.delete(key)

    def _cache_workspace_documents(self, workspace_id: int, documents: list[Document]) -> None:
        """Cache workspace documents list."""
        if not self.cache:
            return
        key = f"workspace:{workspace_id}:documents"
        value = json.dumps([doc.id for doc in documents])
        self.cache.set(key, value, ttl=180)  # Cache for 3 minutes

    def _get_cached_workspace_documents(self, workspace_id: int) -> list[Document] | None:
        """Get workspace documents from cache."""
        if not self.cache:
            return None
        key = f"workspace:{workspace_id}:documents"
        cached = self.cache.get(key)
        if not cached:
            return None
        try:
            doc_ids = json.loads(cached)
            documents = []
            for doc_id in doc_ids:
                doc = self._get_cached_document(doc_id)
                if not doc:
                    # If any document is missing from cache, invalidate the whole list
                    return None
                documents.append(doc)
            return documents
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _invalidate_workspace_documents_cache(self, workspace_id: int) -> None:
        """Invalidate workspace documents list cache."""
        if not self.cache:
            return
        key = f"workspace:{workspace_id}:documents"
        self.cache.delete(key)
