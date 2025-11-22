"""SQL implementation of status repository."""

from sqlalchemy.orm import Session

from shared.models import Document, Workspace
from shared.types.option import Nothing, Option, Some
from shared.types.status import DocumentProcessingStatus, WorkspaceStatus

from .status_repository import StatusRepository


class SqlStatusRepository(StatusRepository):
    """SQL implementation of status repository using Option types."""

    def __init__(self, db: Session) -> None:
        """
        Initialize repository.

        Args:
            db: SQLAlchemy database session
        """
        self._db = db

    def update_document_status(
        self,
        document_id: int,
        status: DocumentProcessingStatus,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> Option[Document]:
        """Update document processing status."""
        document = self._db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return Nothing()

        document.processing_status = status.value
        if error is not None:
            document.processing_error = error
        if chunk_count is not None:
            document.chunk_count = chunk_count

        self._db.commit()
        self._db.refresh(document)
        return Some(document)

    def update_workspace_status(
        self,
        workspace_id: int,
        status: WorkspaceStatus,
        message: str | None = None,
    ) -> Option[Workspace]:
        """Update workspace provisioning status."""
        workspace = (
            self._db.query(Workspace).filter(Workspace.id == workspace_id).first()
        )
        if not workspace:
            return Nothing()

        workspace.status = status.value
        if message is not None:
            workspace.status_message = message

        self._db.commit()
        self._db.refresh(workspace)
        return Some(workspace)
