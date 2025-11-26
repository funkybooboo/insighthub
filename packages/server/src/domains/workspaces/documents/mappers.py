"""Mappers for converting between document models and DTOs."""

from src.infrastructure.models import Document

from .dtos import DocumentResponse


class DocumentMapper:
    """Handles conversions between document domain models and DTOs."""

    @staticmethod
    def document_to_dto(document: Document) -> DocumentResponse:
        """
        Convert a Document model to DocumentResponse DTO.

        Args:
            document: Document model instance

        Returns:
            DocumentResponse DTO
        """
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            mime_type=document.mime_type,
            chunk_count=document.chunk_count,
            processing_status=document.processing_status,
            processing_error=document.processing_error,
            created_at=document.created_at,
        )

    @staticmethod
    def documents_to_dtos(documents: list[Document]) -> list[DocumentResponse]:
        """
        Convert a list of Document models to DocumentResponse DTOs.

        Args:
            documents: List of Document model instances

        Returns:
            List of DocumentResponse DTOs
        """
        return [DocumentMapper.document_to_dto(document) for document in documents]
