"""Document parser interface for Vector RAG."""

from abc import ABC, abstractmethod
from typing import Any

from shared.types import Document


class DocumentParser(ABC):
    """
    Converts raw document bytes into structured Document objects.

    Implementations should handle PDFs, HTML, DOCX, plain text, etc.
    """

    @abstractmethod
    def parse(self, raw: bytes, metadata: dict[str, Any] | None = None) -> Document:
        """
        Parse raw document bytes into a Document.

        Args:
            raw: Binary content of the document
            metadata: Optional metadata to attach to the document

        Returns:
            Document object containing text and metadata
        """
        raise NotImplementedError
