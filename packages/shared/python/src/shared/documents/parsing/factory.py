"""Parser factory for automatically selecting appropriate document parser."""

from typing import BinaryIO, Optional

from shared.documents.parsing.document_parser import DocumentParser, ParsingError
from shared.documents.parsing.docx_document_parser import DocxDocumentParser
from shared.documents.parsing.html_document_parser import HTMLDocumentParser
from shared.documents.parsing.pdf_document_parser import PDFDocumentParser
from shared.documents.parsing.text_document_parser import TextDocumentParser
from shared.types.common import MetadataDict
from shared.types.document import Document
from shared.types.result import Err, Result


class ParserFactory:
    """Factory for creating document parsers based on file format."""

    def __init__(self) -> None:
        """Initialize parser factory with default parsers."""
        self._parsers: list[DocumentParser] = [
            PDFDocumentParser(),
            DocxDocumentParser(),
            HTMLDocumentParser(parser_type="html.parser"),
            TextDocumentParser(),
        ]

    def register_parser(self, parser: DocumentParser) -> None:
        """
        Register a new parser with the factory.

        Args:
            parser: Document parser to register
        """
        self._parsers.append(parser)

    def get_parser(self, filename: str) -> Optional[DocumentParser]:
        """
        Get appropriate parser for the given filename.

        Args:
            filename: Name of the file to parse

        Returns:
            DocumentParser if a parser supports the format, None otherwise
        """
        for parser in self._parsers:
            if parser.supports_format(filename):
                return parser
        return None

    def parse_document(
        self,
        raw: BinaryIO,
        filename: str,
        metadata: MetadataDict | None = None,
    ) -> Result[Document, ParsingError]:
        """
        Parse document using appropriate parser.

        Args:
            raw: Binary document content
            filename: Name of the file
            metadata: Optional metadata to attach

        Returns:
            Result containing Document on success, or ParsingError on failure
        """
        parser = self.get_parser(filename)
        if parser is None:
            return Err(
                ParsingError(
                    f"No parser available for file: {filename}",
                    code="UNSUPPORTED_FORMAT",
                )
            )

        return parser.parse(raw, metadata)

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported file formats.

        Returns:
            List of supported file extensions
        """
        formats: list[str] = []
        test_files = ["test.pdf", "test.docx", "test.html", "test.txt"]

        for test_file in test_files:
            parser = self.get_parser(test_file)
            if parser is not None:
                ext = test_file.lower().split(".")[-1]
                if ext not in formats:
                    formats.append(ext)

        return formats


parser_factory = ParserFactory()
