"""Document data access layer - coordinates cache and repository."""

import json
from datetime import datetime
from typing import Optional

from src.domains.workspace.document.models import Document
from src.domains.workspace.document.repositories import DocumentRepository
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class DocumentDataAccess:
    """Data access layer for Document - handles caching + persistence."""

    def __init__(self, repository: DocumentRepository, cache: Optional[Cache] = None):
        """Initialize data access layer.

        Args:
            repository: Document repository for database operations
            cache: Optional cache for performance optimization
        """
        self.repository = repository  # Exposed for operations not handled by this layer
        self.cache = cache

    def get_by_id(self, document_id: int) -> Document | None:
        """Get document by ID with caching.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        # Try cache first
        cache_key = f"document:{document_id}"
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
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
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Cache deserialization error for document {document_id}: {e}")

        # Cache miss - fetch from database
        document = self.repository.get_by_id(document_id)

        if document and self.cache:
            self._cache_document(document)

        return document

    def get_by_workspace(self, workspace_id: int) -> list[Document]:
        """Get all documents for a workspace with caching.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of documents
        """
        # Try cache first for the document list
        cache_key = f"workspace:{workspace_id}:documents"
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                doc_ids = json.loads(cached_json)
                documents = []
                for doc_id in doc_ids:
                    doc = self.get_by_id(doc_id)  # Uses individual document cache
                    if not doc:
                        # If any document is missing, invalidate list and refetch
                        self._invalidate_workspace_documents_cache(workspace_id)
                        break
                    documents.append(doc)
                else:
                    # All documents found in cache
                    return documents
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        # Cache miss - fetch from database
        documents = self.repository.get_by_workspace(workspace_id)

        # Cache the result
        if self.cache:
            self._cache_workspace_documents(workspace_id, documents)
            # Also cache individual documents
            for doc in documents:
                self._cache_document(doc)

        return documents

    def create(
        self,
        workspace_id: int,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        content_hash: str,
        chunk_count: int,
        status: str,
    ) -> Document:
        """Create a new document.

        Args:
            workspace_id: Workspace ID
            filename: Document filename
            file_path: Path to file in blob storage
            file_size: File size in bytes
            mime_type: MIME type
            content_hash: Content hash
            chunk_count: Number of chunks
            status: Initial status

        Returns:
            Created document
        """
        result = self.repository.create(
            workspace_id=workspace_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            content_hash=content_hash,
            chunk_count=chunk_count,
            status=status,
        )

        if isinstance(result, Exception):
            raise result

        document = result.unwrap()

        if document and self.cache:
            self._cache_document(document)
            self._invalidate_workspace_documents_cache(workspace_id)

        return document

    def update(
        self,
        document_id: int,
        chunk_count: Optional[int] = None,
        status: Optional[str] = None,
    ) -> bool:
        """Update document.

        Args:
            document_id: Document ID
            chunk_count: Optional new chunk count
            status: Optional new status

        Returns:
            True if updated successfully
        """
        result = self.repository.update(document_id, chunk_count, status)
        if result:
            self._invalidate_cache(document_id)
        return result

    def delete(self, document_id: int) -> bool:
        """Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted successfully
        """
        # Get document to find workspace_id before deleting
        document = self.get_by_id(document_id)
        workspace_id = document.workspace_id if document else None

        result = self.repository.delete(document_id)
        if result:
            self._invalidate_cache(document_id)
            if workspace_id:
                self._invalidate_workspace_documents_cache(workspace_id)
        return result

    def _cache_document(self, document: Document) -> None:
        """Cache document data.

        Args:
            document: Document to cache
        """
        if not self.cache:
            return

        cache_key = f"document:{document.id}"
        cache_value = json.dumps(
            {
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
            }
        )
        self.cache.set(cache_key, cache_value, ttl=300)  # Cache for 5 minutes

    def _invalidate_cache(self, document_id: int) -> None:
        """Invalidate document cache.

        Args:
            document_id: Document ID to invalidate
        """
        if self.cache:
            cache_key = f"document:{document_id}"
            self.cache.delete(cache_key)

    def _cache_workspace_documents(self, workspace_id: int, documents: list[Document]) -> None:
        """Cache workspace documents list.

        Args:
            workspace_id: Workspace ID
            documents: List of documents to cache
        """
        if not self.cache:
            return

        cache_key = f"workspace:{workspace_id}:documents"
        cache_value = json.dumps([doc.id for doc in documents])
        self.cache.set(cache_key, cache_value, ttl=180)  # Cache for 3 minutes

    def _invalidate_workspace_documents_cache(self, workspace_id: int) -> None:
        """Invalidate workspace documents list cache.

        Args:
            workspace_id: Workspace ID
        """
        if self.cache:
            cache_key = f"workspace:{workspace_id}:documents"
            self.cache.delete(cache_key)
