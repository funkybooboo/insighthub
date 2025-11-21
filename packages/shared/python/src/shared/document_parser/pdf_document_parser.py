"""Document parser implementation for multiple file formats."""

from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any, List, Optional, Union

from shared.parsing.document_parser import DocumentParser
from shared.types.document import Document
from shared.types.common import PrimitiveValue, MetadataValue

try:
    import pypdf
    from docx import Document as DocxDocument
except ImportError:
    pypdf = None
    DocxDocument = None

import os
import tempfile
from pathlib import Path


class PDFDocumentParser(DocumentParser):
    """PDF document parser using PyPDF2 library."""

    def __init__(self):
        """Initialize PDF parser."""
        pass

    def parse(self, raw: BinaryIO, metadata: dict[str, Any] | None = None) -> Document:
        """
        Parse PDF document bytes into structured Document.

        Args:
            raw: Binary PDF content
            metadata: Optional metadata to attach

        Returns:
            Document: Structured document with text and metadata

        Raises:
            DocumentParsingError: If PDF parsing fails
        """
        if not pypdf:
            raise DocumentParsingError("PyPDF2 library not available for PDF parsing")

        try:
            reader = pypdf.PdfReader(raw)

            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            text_content = "\n".join(text_parts)

            # Extract metadata from PDF
            pdf_metadata = self._extract_pdf_metadata(reader, metadata)

            return Document(
                id=self._generate_document_id(metadata),
                workspace_id=metadata.get("workspace_id", "default") if metadata else "default",
                title=metadata.get("title", self._extract_title_from_metadata(
                    pdf_metadata)) if metadata else self._extract_title_from_metadata(pdf_metadata),
                content=text_content,
                metadata={
                    **pdf_metadata,
                    "file_type": "pdf",
                    "page_count": len(reader.pages),
                    "char_count": len(text_content),
                }
            )

        except Exception as e:
            raise DocumentParsingError(f"Failed to parse PDF: {str(e)}") from e

    def supports_format(self, filename: str) -> bool:
        """
        Check if parser supports the file format.

        Args:
            filename: Name of the file to check

        Returns:
            bool: True if PDF format is supported
        """
        return filename.lower().endswith('.pdf')

    def extract_metadata(self, raw: BinaryIO) -> dict[str, Any]:
        """
        Extract metadata from raw PDF bytes.

        Args:
            raw: Binary PDF content

        Returns:
            dict: Extracted metadata
        """
        if not pypdf:
            return {}

        try:
            reader = pypdf.PdfReader(raw)
            return self._extract_pdf_metadata(reader, None)
        except Exception:
            return {}

    def _extract_pdf_metadata(self, reader: Any, user_metadata: dict[str, Any] | None) -> dict[str, Any]:
        """
        Extract metadata from PDF reader.

        Args:
            reader: PyPDF2 reader object
            user_metadata: User-provided metadata

        Returns:
            Dict[str, Any]: Extracted metadata
        """
        metadata: dict[str, Any] = {}

        # Basic PDF info
        if reader.pages:
            metadata.update({
                "page_count": len(reader.pages),
                "is_encrypted": getattr(reader, 'is_encrypted', False),
                "has_xfa": getattr(reader, '_has_xfa', False),
                "has_xfa_signatures": getattr(reader, '_has_xfa_signatures', False),
            })

        # Document info
        if hasattr(reader, 'documentInfo') and reader.documentInfo:
            doc_info = reader.documentInfo
            if doc_info:
                metadata.update({
                    "title": doc_info.get('/Title'),
                    "author": doc_info.get('/Author'),
                    "subject": doc_info.get('/Subject'),
                    "creator": doc_info.get('/Creator'),
                    "producer": doc_info.get('/Producer'),
                    "creation_date": doc_info.get('/CreationDate'),
                    "modification_date": doc_info.get('/ModDate'),
                    "keywords": doc_info.get('/Keywords'),
                })

        # Include user metadata
        if user_metadata:
            metadata.update(user_metadata)

        return metadata

    def _extract_title_from_metadata(self, metadata: dict[str, Any]) -> str | None:
        """Extract title from PDF metadata."""
        # Try multiple fields for title
        title = metadata.get("title")
        if title:
            return str(title)

        title = metadata.get("subject")
        if title:
            return str(title)

        return None

    def _generate_document_id(self, metadata: dict[str, Any] | None) -> str:
        """Generate document ID from metadata or use default."""
        if metadata and "document_id" in metadata:
            return str(metadata["document_id"])

        import uuid
        return str(uuid.uuid4())
