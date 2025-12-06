"""Document service implementation."""

import json
from datetime import datetime
from io import BytesIO
from typing import Any, Optional

from returns.result import Failure, Result, Success

from src.config import config
from src.domains.workspace.document.data_access import DocumentDataAccess
from src.domains.workspace.document.models import Document, DocumentStatus
from src.domains.workspace.models import Workspace
from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.logger import create_logger
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
    ):
        """Initialize service with data access, workspace repository, and storage.

        Args:
            data_access: Document data access layer (handles cache + repository)
            workspace_repository: Workspace repository (needed for RAG config)
            blob_storage: Blob storage implementation (needed for file operations)
        """
        self.data_access = data_access
        self.workspace_repository = workspace_repository
        self.blob_storage = blob_storage

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
        try:
            self.blob_storage.upload(blob_key, file_content, mime_type)
            logger.info(f"Document uploaded to blob storage: blob_key='{blob_key}'")
        except Exception as e:
            logger.error(f"Blob storage upload failed: {e}")
            return Failure(StorageError(str(e), operation="upload"))

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
            try:
                self.blob_storage.delete(blob_key)
            except Exception:
                pass
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
        base_config: dict[str, Any] = {
            "rag_type": workspace.rag_type,
            "parser_type": "text",  # Auto-detect based on file type
        }

        if workspace.rag_type == "vector":
            # Get workspace-specific vector RAG config
            vector_config = self.workspace_repository.get_vector_rag_config(workspace.id)

            if vector_config:
                base_config.update(
                    {
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
                    }
                )
            else:
                # Fallback to defaults if no config found
                base_config.update(
                    {
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
                    }
                )
        elif workspace.rag_type == "graph":
            # Get workspace-specific graph RAG config
            graph_config = self.workspace_repository.get_graph_rag_config(workspace.id)

            if graph_config:
                base_config.update(
                    {
                        "entity_extraction_algorithm": graph_config.entity_extraction_algorithm,
                        "relationship_extraction_algorithm": graph_config.relationship_extraction_algorithm,
                        "clustering_algorithm": graph_config.clustering_algorithm,
                    }
                )
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
            try:
                self.blob_storage.delete(document.file_path)
                logger.info(f"Document deleted from blob storage: {document.file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete from blob storage: {e}")

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

    def get_document_by_id(self, document_id: int) -> Document | None:
        """Get document by ID with caching (handled by data access layer).

        Args:
            document_id: Document ID

        Returns:
            Optional[Document]: Document if found, None otherwise
        """
        return self.data_access.get_by_id(document_id)
