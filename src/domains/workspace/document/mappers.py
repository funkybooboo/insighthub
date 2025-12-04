"""Mappers for converting between document models and DTOs."""

from src.domains.workspace.document.dtos import DocumentResponse
from src.domains.workspace.document.models import Document
from src.infrastructure.mappers import format_datetime


class DocumentMapper:
    """Handles conversions between document domain models and Response DTOs."""

    @staticmethod
    def to_response(document: Document) -> DocumentResponse:
        """
        Convert a Document model to DocumentResponse DTO.

        Args:
            document: Document model instance

        Returns:
            DocumentResponse DTO
        """
        return DocumentResponse(
            id=document.id,
            workspace_id=document.workspace_id,
            filename=document.filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            chunk_count=document.chunk_count,
            status=document.status,
            content_hash=document.content_hash,
            created_at=format_datetime(document.created_at),
        )
