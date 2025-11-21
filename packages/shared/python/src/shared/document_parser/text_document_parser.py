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


class TextDocumentParser(DocumentParser):
    """Plain text document parser."""

    def __init__(self):
        """Initialize text parser."""
        pass

    def parse(self, raw: BinaryIO, metadata: dict[str, Any] | None = None) -> Document:
        """
        Parse text document bytes into structured Document.

        Args:
            raw: Binary text content
            metadata: Optional metadata to attach

        Returns:
            Document: Structured document with text and metadata

        Raises:
            DocumentParsingError: If text parsing fails
        """
        try:
            # Seek to beginning
            raw.seek(0)

            # Read and decode text
            content = raw.read().decode('utf-8')

            # Extract metadata
            text_metadata = self._extract_text_metadata(content, metadata)

            return Document(
                id=self._generate_document_id(metadata),
                workspace_id=metadata.get("workspace_id", "default") if metadata else "default",
                title=metadata.get("title", self._extract_title_from_content(
                    content)) if metadata else self._extract_title_from_content(content),
                content=content,
                metadata={
                    **text_metadata,
                    "file_type": "text",
                    "char_count": len(content),
                    "line_count": len(content.splitlines()),
                    "word_count": len(content.split()),
                }
            )

        except Exception as e:
            raise DocumentParsingError(f"Failed to parse text: {str(e)}") from e

    def supports_format(self, filename: str) -> bool:
        """
        Check if parser supports the file format.

        Args:
            filename: Name of the file to check

        Returns:
            bool: True if text format is supported
        """
        return filename.lower().endswith('.txt')

    def extract_metadata(self, raw: BinaryIO) -> dict[str, Any]:
        """
        Extract metadata from raw text bytes.

        Args:
            raw: Binary text content

        Returns:
            dict: Extracted metadata
        """
        try:
            raw.seek(0)
            content = raw.read().decode('utf-8')
            return self._extract_text_metadata(content, None)
        except Exception:
            return {}

    def _extract_text_metadata(self, content: str, user_metadata: dict[str, Any] | None) -> dict[str, Any]:
        """
        Extract metadata from text content.

        Args:
            content: Text content
            user_metadata: User-provided metadata

        Returns:
            Dict[str, Any]: Extracted metadata
        """
        metadata: dict[str, Any] = {
            "encoding": "utf-8",
        }

        # Basic text statistics
        if content:
            lines = content.splitlines()
            words = content.split()

            metadata.update({
                "line_count": len(lines),
                "word_count": len(words),
                "char_count": len(content),
                "has_content": len(content.strip()) > 0,
            })

            # Try to extract potential title from first line
            if lines and len(lines[0].strip()) > 0:
                first_line = lines[0].strip()
                if len(first_line) < 100:  # Reasonable title length
                    metadata["potential_title"] = first_line

        # Include user metadata
        if user_metadata:
            metadata.update(user_metadata)

        return metadata

    def _extract_title_from_content(self, content: str) -> str | None:
        """Extract title from text content."""
        lines = content.splitlines()

        # Look for first non-empty line as potential title
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) < 100:  # Reasonable title length
                return stripped

        return None

    def _generate_document_id(self, metadata: dict[str, Any] | None) -> str:
        """Generate document ID from metadata or use default."""
        if metadata and "document_id" in metadata:
            return str(metadata["document_id"])

        import uuid
        return str(uuid.uuid4())
