"""Parser factory for automatically selecting appropriate document parser."""

from typing import BinaryIO

from shared.document_parser.document_parser import DocumentParser, ParsingError
from shared.document_parser.docx_document_parser import DocxDocumentParser
from shared.document_parser.html_document_parser import HTMLDocumentParser
from shared.document_parser.pdf_document_parser import PDFDocumentParser
from shared.document_parser.text_document_parser import TextDocumentParser
from shared.types.common import MetadataDict
from shared.types.document import Document
from shared.types.option import Nothing, Option, Some
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

    def get_parser(self, filename: str) -> Option[DocumentParser]:
        """
        Get appropriate parser for the given filename.

        Args:
            filename: Name of the file to parse

        Returns:
            Some(DocumentParser) if a parser supports the format, Nothing() otherwise
        """
        for parser in self._parsers:
            if parser.supports_format(filename):
                return Some(parser)
        return Nothing()

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
        parser_option = self.get_parser(filename)
        if parser_option.is_nothing():
            return Err(
                ParsingError(
                    f"No parser available for file: {filename}",
                    code="UNSUPPORTED_FORMAT",
                )
            )

        parser = parser_option.unwrap()
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
            parser_option = self.get_parser(test_file)
            if parser_option.is_some():
                ext = test_file.lower().split(".")[-1]
                if ext not in formats:
                    formats.append(ext)

        return formats


parser_factory = ParserFactory()
