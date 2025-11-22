"""Document parsing for various file formats."""

from shared.document_parser.document_parser import DocumentParser, ParsingError
from shared.document_parser.docx_document_parser import DocxDocumentParser
from shared.document_parser.html_document_parser import HTMLDocumentParser
from shared.document_parser.parser_factory import ParserFactory, parser_factory
from shared.document_parser.pdf_document_parser import PDFDocumentParser
from shared.document_parser.text_document_parser import TextDocumentParser

__all__ = [
    "DocumentParser",
    "ParsingError",
    "PDFDocumentParser",
    "TextDocumentParser",
    "DocxDocumentParser",
    "HTMLDocumentParser",
    "ParserFactory",
    "factory.py",
]
