"""Status repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from shared.models import Document, Workspace
from shared.types.status import DocumentProcessingStatus, WorkspaceStatus


class StatusRepository(ABC):
    """
    Abstract base class for status repository.
    """

    @abstractmethod
    def update_document_status(
        self,
        document_id: int,
        status: DocumentProcessingStatus,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> Optional[Document]:
        """
        Update document processing status.

        Args:
            document_id: Document ID
            status: New processing status
            error: Optional error message (for FAILED status)
            chunk_count: Optional chunk count (for READY status)

        Returns:
            Document if found and updated, None if not found
        """
        pass

    @abstractmethod
    def update_workspace_status(
        self,
        workspace_id: int,
        status: WorkspaceStatus,
        message: str | None = None,
    ) -> Optional[Workspace]:
        """
        Update workspace provisioning status.

        Args:
            workspace_id: Workspace ID
            status: New workspace status
            message: Optional status message

        Returns:
            Workspace if found and updated, None if not found
        """
        pass
