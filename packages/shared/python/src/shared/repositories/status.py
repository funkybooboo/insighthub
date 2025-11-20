"""Repository interfaces and implementations for status updates."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from shared.models import Document, Workspace
from shared.types.option import Option, Some, Nothing, from_nullable
from shared.types.status import DocumentProcessingStatus, WorkspaceStatus


class StatusRepository(ABC):
    """
    Abstract base class for status repository.
    
    Uses Option[T] instead of T | None to make intent explicit.
    """

    @abstractmethod
    def update_document_status(
        self,
        document_id: int,
        status: DocumentProcessingStatus,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> Option[Document]:
        """
        Update document processing status.

        Args:
            document_id: Document ID
            status: New processing status
            error: Optional error message (for FAILED status)
            chunk_count: Optional chunk count (for READY status)

        Returns:
            Option[Document]: Some(document) if found and updated, Nothing() if not found
        """
        pass

    @abstractmethod
    def update_workspace_status(
        self,
        workspace_id: int,
        status: WorkspaceStatus,
        message: str | None = None,
    ) -> Option[Workspace]:
        """
        Update workspace provisioning status.

        Args:
            workspace_id: Workspace ID
            status: New workspace status
            message: Optional status message

        Returns:
            Option[Workspace]: Some(workspace) if found and updated, Nothing() if not found
        """
        pass


class SqlStatusRepository(StatusRepository):
    """SQL implementation of status repository using Option types."""

    def __init__(self, db: Session):
        """
        Initialize repository.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def update_document_status(
        self,
        document_id: int,
        status: DocumentProcessingStatus,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> Option[Document]:
        """
        Update document processing status.
        
        Returns Option[Document] instead of Document | None for clarity.
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return Nothing()

        document.processing_status = status.value
        if error is not None:
            document.processing_error = error
        if chunk_count is not None:
            document.chunk_count = chunk_count

        self.db.commit()
        self.db.refresh(document)
        return Some(document)

    def update_workspace_status(
        self,
        workspace_id: int,
        status: WorkspaceStatus,
        message: str | None = None,
    ) -> Option[Workspace]:
        """
        Update workspace provisioning status.
        
        Returns Option[Workspace] instead of Workspace | None for clarity.
        """
        workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            return Nothing()

        workspace.status = status.value
        if message is not None:
            workspace.status_message = message

        self.db.commit()
        self.db.refresh(workspace)
        return Some(workspace)
