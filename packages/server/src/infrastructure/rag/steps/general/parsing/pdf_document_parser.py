"""PDF document parser implementation."""

import uuid
from typing import TYPE_CHECKING, BinaryIO

from src.infrastructure.rag.steps.general.parsing.document_parser import (
    DocumentParser,
    ParsingError,
)
from src.infrastructure.types.common import MetadataDict
from src.infrastructure.types.document import Document
from src.infrastructure.types.result import Err, Ok, Result

if TYPE_CHECKING:
    import pypdf as pypdf_module

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    pypdf = None
    PYPDF_AVAILABLE = False


class PDFDocumentParser(DocumentParser):
    """PDF document parser using pypdf library."""

    def parse(
        self, raw: BinaryIO, metadata: MetadataDict | None = None
    ) -> Result[Document, ParsingError]:
        """
        Parse PDF document bytes into structured Document.

        Args:
            raw: Binary PDF content
            metadata: Optional metadata to attach

        Returns:
            Result containing Document on success, or ParsingError on failure
        """
        if not PYPDF_AVAILABLE or pypdf is None:
            return Err(
                ParsingError(
                    "pypdf library not available for PDF parsing",
                    code="DEPENDENCY_ERROR",
                )
            )

        try:
            reader = pypdf.PdfReader(raw)

            text_parts: list[str] = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            text_content = "\n".join(text_parts)

            pdf_metadata = self._extract_pdf_metadata(reader, metadata)
            doc_id = self._generate_document_id(metadata)
            workspace_id = str(metadata.get("workspace_id", "default")) if metadata else "default"
            title = self._get_title(metadata, pdf_metadata)

            return Ok(
                Document(
                    id=doc_id,
                    workspace_id=workspace_id,
                    title=title,
                    content=text_content,
                    metadata={
                        "file_type": "pdf",
                        "page_count": str(len(reader.pages)),
                        "char_count": str(len(text_content)),
                    },
                )
            )

        except Exception as e:
            return Err(ParsingError(f"Failed to parse PDF: {e}", code="PARSE_ERROR"))

    def supports_format(self, filename: str) -> bool:
        """Check if parser supports the file format."""
        return filename.lower().endswith(".pdf")

    def extract_metadata(self, raw: BinaryIO) -> MetadataDict:
        """Extract metadata from raw PDF bytes."""
        if not PYPDF_AVAILABLE or pypdf is None:
            return {}

        try:
            reader = pypdf.PdfReader(raw)
            return self._extract_pdf_metadata(reader, None)
        except Exception:
            return {}

    def _extract_pdf_metadata(
        self,
        reader: "pypdf_module.PdfReader",
        user_metadata: MetadataDict | None,
    ) -> MetadataDict:
        """Extract metadata from PDF reader."""
        metadata: MetadataDict = {}

        if reader.pages:
            metadata["page_count"] = len(reader.pages)
            metadata["is_encrypted"] = getattr(reader, "is_encrypted", False)

        if hasattr(reader, "metadata") and reader.metadata:
            doc_info = reader.metadata
            if doc_info:
                if doc_info.title:
                    metadata["title"] = str(doc_info.title)
                if doc_info.author:
                    metadata["author"] = str(doc_info.author)
                if doc_info.subject:
                    metadata["subject"] = str(doc_info.subject)
                if doc_info.creator:
                    metadata["creator"] = str(doc_info.creator)

        if user_metadata:
            metadata.update(user_metadata)

        return metadata

    def _get_title(self, metadata: MetadataDict | None, pdf_metadata: MetadataDict) -> str | None:
        """Get title from metadata or PDF metadata."""
        if metadata and "title" in metadata:
            return str(metadata["title"])

        title = pdf_metadata.get("title")
        if title:
            return str(title)

        subject = pdf_metadata.get("subject")
        if subject:
            return str(subject)

        return None

    def _generate_document_id(self, metadata: MetadataDict | None) -> str:
        """Generate document ID from metadata or use default."""
        if metadata and "document_id" in metadata:
            return str(metadata["document_id"])
        return str(uuid.uuid4())
