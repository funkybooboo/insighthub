"""Text document parser implementation."""

import uuid
from typing import Optional, BinaryIO

from returns.result import Failure, Result, Success

from src.infrastructure.rag.steps.general.parsing.document_parser import (
    DocumentParser,
    ParsingError,
)
from src.infrastructure.types.common import MetadataDict
from src.infrastructure.types.document import Document


class TextDocumentParser(DocumentParser):
    """Plain text document parser."""

    def parse(
        self, raw: BinaryIO, metadata: Optional[MetadataDict]= None
    ) -> Result[Document, ParsingError]:
        """
        Parse text document bytes into structured Document.

        Args:
            raw: Binary text content
            metadata: Optional metadata to attach

        Returns:
            Result containing Document on success, or ParsingError on failure
        """
        try:
            raw.seek(0)
            content = raw.read().decode("utf-8")

            self._extract_text_metadata(content, metadata)
            doc_id = self._generate_document_id(metadata)
            workspace_id = str(metadata.get("workspace_id", "default")) if metadata else "default"
            title = self._get_title(metadata, content) or "Untitled Document"
            return Success(
                Document(
                    id=doc_id,
                    workspace_id=workspace_id,
                    title=title,
                    content=content,
                    metadata={
                        "file_type": "text",
                        "char_count": str(len(content)),
                        "line_count": str(len(content.splitlines())),
                        "word_count": str(len(content.split())),
                    },
                )
            )

        except UnicodeDecodeError as e:
            return Failure(ParsingError(f"Failed to decode text: {e}", code="ENCODING_ERROR"))
        except Exception as e:
            return Failure(ParsingError(f"Failed to parse text: {e}", code="PARSE_ERROR"))

    def supports_format(self, filename: str) -> bool:
        """Check if parser supports the file format."""
        return filename.lower().endswith(".txt")

    def extract_metadata(self, raw: BinaryIO) -> MetadataDict:
        """Extract metadata from raw text bytes."""
        try:
            raw.seek(0)
            content = raw.read().decode("utf-8")
            return self._extract_text_metadata(content, None)
        except Exception:
            return {}

    def _extract_text_metadata(
        self, content: str, user_metadata: Optional[MetadataDict]) -> MetadataDict:
        """Extract metadata from text content."""
        metadata: MetadataDict = {
            "encoding": "utf-8",
        }

        if content:
            lines = content.splitlines()
            words = content.split()

            metadata["line_count"] = len(lines)
            metadata["word_count"] = len(words)
            metadata["char_count"] = len(content)
            metadata["has_content"] = len(content.strip()) > 0

            if lines and len(lines[0].strip()) > 0:
                first_line = lines[0].strip()
                if len(first_line) < 100:
                    metadata["potential_title"] = first_line

        if user_metadata:
            metadata.update(user_metadata)

        return metadata

    def _get_title(self, metadata: Optional[MetadataDict], content: str) -> Optional[str]:
        """Get title from metadata or extract from content."""
        if metadata and "title" in metadata:
            return str(metadata["title"])

        lines = content.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) < 100:
                return stripped

        return None

    def _generate_document_id(self, metadata: Optional[MetadataDict]) -> str:
        """Generate document ID from metadata or use default."""
        if metadata and "document_id" in metadata:
            return str(metadata["document_id"])
        return str(uuid.uuid4())
