"""Document parsing for various file formats."""

from shared.documents.parsing.document_parser import DocumentParser, ParsingError
from shared.documents.parsing.docx_document_parser import DocxDocumentParser
from shared.documents.parsing.factory import ParserFactory, parser_factory
from shared.documents.parsing.html_document_parser import HTMLDocumentParser
from shared.documents.parsing.pdf_document_parser import PDFDocumentParser
from shared.documents.parsing.text_document_parser import TextDocumentParser

__all__ = [
    "DocumentParser",
    "ParsingError",
    "PDFDocumentParser",
    "TextDocumentParser",
    "DocxDocumentParser",
    "HTMLDocumentParser",
    "ParserFactory",
    "parser_factory",
]
