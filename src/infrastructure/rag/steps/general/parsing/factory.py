"""Parser factory for automatically selecting appropriate document parser."""

from typing import BinaryIO, Optional

from returns.result import Failure, Result

from src.infrastructure.rag.steps.general.parsing.document_parser import (
    DocumentParser,
    ParsingError,
)
from src.infrastructure.rag.steps.general.parsing.docx_document_parser import DocxDocumentParser
from src.infrastructure.rag.steps.general.parsing.html_document_parser import HTMLDocumentParser
from src.infrastructure.rag.steps.general.parsing.pdf_document_parser import PDFDocumentParser
from src.infrastructure.rag.steps.general.parsing.text_document_parser import TextDocumentParser
from src.infrastructure.types.common import MetadataDict
from src.infrastructure.types.document import Document


class ParserFactory:
    """Factory for creating document parsers based on file format."""

    _AVAILABLE_PARSERS = {
        "pdf": {
            "class": PDFDocumentParser,
            "label": "PDF",
            "description": "Parse PDF document",
        },
        "docx": {
            "class": DocxDocumentParser,
            "label": "DOCX",
            "description": "Parse Microsoft Word document",
        },
        "html": {
            "class": HTMLDocumentParser,
            "label": "HTML",
            "description": "Parse HTML document",
        },
        "text": {
            "class": TextDocumentParser,
            "label": "Text",
            "description": "Parse plain text document",
        },
    }

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
        metadata: Optional[MetadataDict] = None,
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
            return Failure(
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

    @staticmethod
    def get_available_parsers() -> list[dict[str, str]]:
        """Get list of available parser implementations."""
        return [
            {
                "value": key,
                "label": str(info["label"]),
                "description": str(info["description"]),
            }
            for key, info in ParserFactory._AVAILABLE_PARSERS.items()
        ]

    @staticmethod
    def create_parser(parser_type: str) -> DocumentParser:
        """Create a parser instance based on type.

        Args:
            parser_type: Type of parser to create

        Returns:
            DocumentParser instance

        Raises:
            ValueError: If parser_type is not supported
        """
        parser_info = ParserFactory._AVAILABLE_PARSERS.get(parser_type)
        if parser_info is None:
            available = list(ParserFactory._AVAILABLE_PARSERS.keys())
            raise ValueError(
                f"Unsupported parser type: {parser_type}. "
                f"Available parsers: {', '.join(available)}"
            )

        parser_class = parser_info["class"]
        if parser_class == HTMLDocumentParser:
            return HTMLDocumentParser(parser_type="html.parser")
        elif parser_class == PDFDocumentParser:
            return PDFDocumentParser()
        elif parser_class == DocxDocumentParser:
            return DocxDocumentParser()
        elif parser_class == TextDocumentParser:
            return TextDocumentParser()
        else:
            raise ValueError(f"Unknown parser class: {parser_class}")


parser_factory = ParserFactory()


def get_supported_extensions() -> set[str]:
    """Get set of supported file extensions from global parser factory."""
    return set(parser_factory.get_supported_formats())
