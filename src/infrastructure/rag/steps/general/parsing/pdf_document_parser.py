"""PDF document parser implementation."""

import uuid
from typing import TYPE_CHECKING, BinaryIO, Optional

from returns.result import Failure, Result, Success

from src.infrastructure.rag.steps.general.parsing.document_parser import (
    DocumentParser,
    ParsingError,
)
from src.infrastructure.types.common import MetadataDict
from src.infrastructure.types.document import Document

if TYPE_CHECKING:
    import pypdf as pypdf_module

try:
    import pypdf

    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class PDFDocumentParser(DocumentParser):
    """PDF document parser using pypdf library."""

    def parse(
        self, raw: BinaryIO, metadata: Optional[MetadataDict] = None
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
            return Failure(
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
            title = self._get_title(metadata, pdf_metadata) or "Untitled Document"

            return Success(
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
            return Failure(ParsingError(f"Failed to parse PDF: {e}", code="PARSE_ERROR"))

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
        user_metadata: Optional[MetadataDict],
    ) -> MetadataDict:
        """Extract metadata from PDF reader."""
        metadata: MetadataDict = {}

        if reader.pages:
            metadata["page_count"] = len(reader.pages)
            metadata["is_encrypted"] = getattr(reader, "is_encrypted", False)

        if hasattr(reader, "metadata") and reader.metadata:
            doc_info_data = self._extract_document_info(reader.metadata)
            metadata.update(doc_info_data)

        if user_metadata:
            metadata.update(user_metadata)

        return metadata

    def _extract_document_info(
        self, doc_info: "pypdf_module.DocumentInformation"
    ) -> MetadataDict:
        """Extract document information fields and return metadata."""
        result: MetadataDict = {}

        if not doc_info:
            return result

        if doc_info.title:
            result["title"] = str(doc_info.title)
        if doc_info.author:
            result["author"] = str(doc_info.author)
        if doc_info.subject:
            result["subject"] = str(doc_info.subject)
        if doc_info.creator:
            result["creator"] = str(doc_info.creator)

        return result

    def _get_title(self, metadata: Optional[MetadataDict], pdf_metadata: MetadataDict) -> Optional[str]:
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

    def _generate_document_id(self, metadata: Optional[MetadataDict]) -> str:
        """Generate document ID from metadata or use default."""
        if metadata and "document_id" in metadata:
            return str(metadata["document_id"])
        return str(uuid.uuid4())
