"""SQL implementation of status repository using PostgresSqlDatabase."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models import Document, Workspace
from shared.types.status import DocumentProcessingStatus, WorkspaceStatus

from .status_repository import StatusRepository


class SqlStatusRepository(StatusRepository):
    """SQL implementation of status repository using direct SQL queries."""

    def __init__(self, db: PostgresSqlDatabase) -> None:
        """
        Initialize repository.

        Args:
            db: PostgresSqlDatabase instance
        """
        self._db = db

    def update_document_status(
        self,
        document_id: int,
        status: DocumentProcessingStatus,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> Optional[Document]:
        """Update document processing status."""
        set_parts = ["processing_status = %(status)s"]
        params: dict[str, object | None] = {"status": status.value, "id": document_id}

        if error is not None:
            set_parts.append("processing_error = %(error)s")
            params["error"] = error
        if chunk_count is not None:
            set_parts.append("chunk_count = %(chunk_count)s")
            params["chunk_count"] = chunk_count

        set_clause = ", ".join(set_parts)
        query = f"""
        UPDATE documents
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING *;
        """

        row = self._db.fetchone(query, params)
        if row is None:
            return None
        return Document(**row)

    def update_workspace_status(
        self,
        workspace_id: int,
        status: WorkspaceStatus,
        message: str | None = None,
    ) -> Optional[Workspace]:
        """Update workspace provisioning status."""
        set_parts = ["status = %(status)s"]
        params: dict[str, object | None] = {"status": status.value, "id": workspace_id}

        if message is not None:
            set_parts.append("status_message = %(message)s")
            params["message"] = message

        set_clause = ", ".join(set_parts)
        query = f"""
        UPDATE workspaces
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING *;
        """

        row = self._db.fetchone(query, params)
        if row is None:
            return None
        return Workspace(**row)
