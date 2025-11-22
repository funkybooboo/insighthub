"""Document parser interface for converting raw bytes to structured Document objects."""

from abc import ABC, abstractmethod
from typing import BinaryIO

from shared.types.common import MetadataDict
from shared.types.document import Document
from shared.types.result import Result


class ParsingError:
    """Error type for document parsing failures."""

    def __init__(self, message: str, code: str = "PARSING_ERROR") -> None:
        """
        Initialize parsing error.

        Args:
            message: Error message
            code: Error code for categorization
        """
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.code}] {self.message}"


class DocumentParser(ABC):
    """
    Interface for parsing raw document bytes into structured Document objects.

    Implementations should handle different file formats (PDF, TXT, DOCX, etc.)
    and extract text content along with metadata.
    """

    @abstractmethod
    def parse(
        self, raw: BinaryIO, metadata: MetadataDict | None = None
    ) -> Result[Document, ParsingError]:
        """
        Parse raw document bytes into a Document object.

        Args:
            raw: Binary content of the document
            metadata: Optional metadata to attach to the document

        Returns:
            Result containing Document on success, or ParsingError on failure
        """
        pass

    @abstractmethod
    def supports_format(self, filename: str) -> bool:
        """
        Check if the parser supports the given file format.

        Args:
            filename: Name of the file to check

        Returns:
            True if format is supported, False otherwise
        """
        pass

    @abstractmethod
    def extract_metadata(self, raw: BinaryIO) -> MetadataDict:
        """
        Extract metadata from raw document bytes.

        Args:
            raw: Binary content of the document

        Returns:
            Extracted metadata (title, author, created_date, etc.)
        """
        pass
