"""Parser factory for automatically selecting appropriate document parser."""

from typing import BinaryIO

from shared.parsing.document_parser import DocumentParser
from shared.types.document import Document
from shared.parsing.parsers import (
    PDFDocumentParser,
    TextDocumentParser,
    DocxDocumentParser,
    DocumentParsingError,
)


class ParserFactory:
    """Factory for creating document parsers based on file format."""

    def __init__(self):
        """Initialize parser factory with default parsers."""
        self._parsers: list[DocumentParser] = [
            PDFDocumentParser(),
            DocxDocumentParser(),
            TextDocumentParser(),
        ]

    def register_parser(self, parser: DocumentParser) -> None:
        """
        Register a new parser with the factory.

        Args:
            parser: Document parser to register
        """
        self._parsers.append(parser)

    def get_parser(self, filename: str) -> DocumentParser:
        """
        Get appropriate parser for the given filename.

        Args:
            filename: Name of the file to parse

        Returns:
            DocumentParser: Parser that supports the file format

        Raises:
            DocumentParsingError: If no parser supports the format
        """
        for parser in self._parsers:
            if parser.supports_format(filename):
                return parser
        
        raise DocumentParsingError(f"No parser available for file: {filename}")

    def parse_document(
        self, 
        raw: BinaryIO, 
        filename: str, 
        metadata: dict[str, str | int | float | bool] | None = None
    ) -> Document:
        """
        Parse document using appropriate parser.

        Args:
            raw: Binary document content
            filename: Name of the file
            metadata: Optional metadata to attach

        Returns:
            Document: Parsed document

        Raises:
            DocumentParsingError: If parsing fails
        """
        parser = self.get_parser(filename)
        return parser.parse(raw, metadata)

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported file formats.

        Returns:
            List[str]: List of supported file extensions
        """
        formats = []
        test_files = [
            "test.pdf",
            "test.docx", 
            "test.txt"
        ]
        
        for test_file in test_files:
            try:
                parser = self.get_parser(test_file)
                if parser.supports_format(test_file):
                    ext = test_file.lower().split('.')[-1]
                    if ext not in formats:
                        formats.append(ext)
            except DocumentParsingError:
                continue
        
        return formats


# Global parser factory instance
parser_factory = ParserFactory()