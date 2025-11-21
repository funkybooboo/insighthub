"""Document parser interface for converting raw bytes to structured Document objects."""

from abc import ABC, abstractmethod
from typing import Any, BinaryIO

from shared.types.document import Document


class DocumentParser(ABC):
    """
    Interface for parsing raw document bytes into structured Document objects.
    
    Implementations should handle different file formats (PDF, TXT, DOCX, etc.)
    and extract text content along with metadata.
    """

    @abstractmethod
    def parse(self, raw: BinaryIO, metadata: dict[str, Any] | None = None) -> Document:
        """
        Parse raw document bytes into a Document object.

        Args:
            raw: Binary content of the document
            metadata: Optional metadata to attach to the document

        Returns:
            Document: Structured document with text and metadata

        Raises:
            DocumentParsingError: If parsing fails
        """
        pass

    @abstractmethod
    def supports_format(self, filename: str) -> bool:
        """
        Check if the parser supports the given file format.

        Args:
            filename: Name of the file to check

        Returns:
            bool: True if format is supported, False otherwise
        """
        pass

    @abstractmethod
    def extract_metadata(self, raw: BinaryIO) -> dict[str, Any]:
        """
        Extract metadata from raw document bytes.

        Args:
            raw: Binary content of the document

        Returns:
            dict: Extracted metadata (title, author, created_date, etc.)
        """
        pass