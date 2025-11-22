"""SQL implementation of status repository using SqlDatabase and Option types."""

from shared.database.sql.sql_database import SqlDatabase
from shared.models import Document, Workspace
from shared.types.option import Nothing, Option, Some
from shared.types.status import DocumentProcessingStatus, WorkspaceStatus

from .status_repository import StatusRepository


class SqlStatusRepository(StatusRepository):
    """SQL implementation of status repository using direct SQL queries."""

    def __init__(self, db: SqlDatabase) -> None:
        """
        Initialize repository.

        Args:
            db: SqlDatabase instance
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
        set_parts = ["processing_status = %(status)s"]
        params = {"status": status.value, "id": document_id}

        if error is not None:
            set_parts.append("processing_error = %(error)s")
            params["error"] = error
        if chunk_count is not None:
            set_parts.append("chunk_count = %(chunk_count)s")
            params["chunk_count"] = chunk_count

        set_clause = ", ".join(set_parts)
        query = f"""
        UPDATE document
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING id, user_id, filename, file_path, file_size, mime_type, content_hash, chunk_count, rag_collection, processing_status, processing_error, created_at, updated_at;
        """

        row = self._db.fetchone(query, params)
        if row is None:
            return Nothing()
        return Some(Document(**row))

    def update_workspace_status(
        self,
        workspace_id: int,
        status: WorkspaceStatus,
        message: str | None = None,
    ) -> Option[Workspace]:
        """Update workspace provisioning status."""
        set_parts = ["status = %(status)s"]
        params = {"status": status.value, "id": workspace_id}

        if message is not None:
            set_parts.append("status_message = %(message)s")
            params["message"] = message

        set_clause = ", ".join(set_parts)
        query = f"""
        UPDATE workspace
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING id, name, status, status_message, created_at, updated_at;
        """

        row = self._db.fetchone(query, params)
        if row is None:
            return Nothing()
        return Some(Workspace(**row))
