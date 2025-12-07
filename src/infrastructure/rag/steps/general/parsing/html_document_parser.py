"""HTML document parser implementation."""

import re
import uuid
from typing import TYPE_CHECKING, BinaryIO, Optional

from returns.result import Failure, Result, Success

from src.infrastructure.rag.steps.general.parsing.document_parser import (
    DocumentParser,
    ParsingError,
)
from src.infrastructure.types.common import MetadataDict
from src.infrastructure.types.document import Document

if TYPE_CHECKING:
    from bs4 import BeautifulSoup as BS4Type
    from bs4 import Tag

try:
    import bs4

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class HTMLDocumentParser(DocumentParser):
    """
    HTML document parser using BeautifulSoup.

    Extracts text content from HTML document, stripping tags and preserving
    structure where possible.

    Example:
        parser = HTMLDocumentParser(parser_type="html.parser")
        with open("document.html", "rb") as f:
            result = parser.parse(f, metadata={"source": "web"})
            if result.is_ok():
                doc = result.unwrap()
    """

    def __init__(self, parser_type: str) -> None:
        """
        Initialize HTML parser.

        Args:
            parser_type: BeautifulSoup parser type ("html.parser", "lxml", "html5lib")
        """
        self._parser_type = parser_type

    def parse(
        self, raw: BinaryIO, metadata: Optional[MetadataDict] = None
    ) -> Result[Document, ParsingError]:
        """
        Parse HTML document bytes into structured Document.

        Args:
            raw: Binary HTML content
            metadata: Optional metadata to attach

        Returns:
            Result containing Document on success, or ParsingError on failure
        """
        if not BS4_AVAILABLE:
            return Failure(
                ParsingError(
                    "BeautifulSoup library not available. Install: pip install beautifulsoup4",
                    code="DEPENDENCY_ERROR",
                )
            )

        try:
            raw.seek(0)
            content = raw.read()

            html_text = self._decode_content(content)
            soup = bs4.BeautifulSoup(html_text, self._parser_type)

            for script_or_style in soup(["script", "style", "noscript"]):
                script_or_style.decompose()

            text_content = soup.get_text(separator="\n", strip=True)
            text_content = self._clean_text(text_content)

            html_metadata = self._extract_html_metadata(soup, metadata)
            doc_id = self._generate_document_id(metadata)
            workspace_id = str(metadata.get("workspace_id", "default")) if metadata else "default"
            title = self._get_title(metadata, html_metadata) or "Untitled Document"

            return Success(
                Document(
                    id=doc_id,
                    workspace_id=workspace_id,
                    title=title,
                    content=text_content,
                    metadata={
                        "file_type": "html",
                        "char_count": str(len(text_content)),
                        "word_count": str(len(text_content.split())),
                    },
                )
            )

        except Exception as e:
            return Failure(ParsingError(f"Failed to parse HTML: {e}", code="PARSE_ERROR"))

    def supports_format(self, filename: str) -> bool:
        """Check if parser supports the file format."""
        lower = filename.lower()
        return lower.endswith(".html") or lower.endswith(".htm")

    def extract_metadata(self, raw: BinaryIO) -> MetadataDict:
        """Extract metadata from raw HTML bytes."""
        if not BS4_AVAILABLE:
            return {}

        try:
            raw.seek(0)
            content = raw.read()
            html_text = self._decode_content(content)
            soup = bs4.BeautifulSoup(html_text, self._parser_type)
            return self._extract_html_metadata(soup, None)
        except Exception:
            return {}

    def _decode_content(self, content: bytes) -> str:
        """Decode HTML content with fallback encodings."""
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        return content.decode("utf-8", errors="replace")

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    def _extract_html_metadata(
        self, soup: "BS4Type", user_metadata: Optional[MetadataDict]
    ) -> MetadataDict:
        """Extract metadata from HTML document."""
        metadata: MetadataDict = {}

        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            metadata["title"] = title_tag.string.strip()

        for meta in soup.find_all("meta"):
            meta_data = self._process_meta_tag(meta)
            metadata.update(meta_data)

        metadata["heading_count"] = len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
        metadata["paragraph_count"] = len(soup.find_all("p"))
        metadata["link_count"] = len(soup.find_all("a"))

        if user_metadata:
            metadata.update(user_metadata)

        return metadata

    def _process_meta_tag(self, meta: "Tag") -> MetadataDict:
        """Process a single meta tag and return metadata."""
        result: MetadataDict = {}

        name_val = meta.get("name", "")
        name = str(name_val).lower() if name_val else ""
        content_val = meta.get("content", "")
        content = str(content_val) if content_val else ""

        if name and content:
            name_data = self._process_meta_name(name, content)
            result.update(name_data)

        property_val = meta.get("property", "")
        property_name = str(property_val).lower() if property_val else ""
        if property_name and content:
            property_data = self._process_meta_property(property_name, content)
            result.update(property_data)

        return result

    def _process_meta_name(self, name: str, content: str) -> MetadataDict:
        """Process meta tag with name attribute and return metadata."""
        if name == "description":
            return {"description": content}
        elif name == "keywords":
            return {"keywords": content}
        elif name == "author":
            return {"author": content}
        return {}

    def _process_meta_property(self, property_name: str, content: str) -> MetadataDict:
        """Process meta tag with property attribute and return metadata."""
        if property_name == "og:title":
            return {"og_title": content}
        elif property_name == "og:description":
            return {"og_description": content}
        return {}

    def _get_title(
        self, metadata: Optional[MetadataDict], html_metadata: MetadataDict
    ) -> Optional[str]:
        """Get title from metadata or HTML metadata."""
        if metadata and "title" in metadata:
            return str(metadata["title"])

        title = html_metadata.get("title")
        if title:
            return str(title)

        return None

    def _generate_document_id(self, metadata: Optional[MetadataDict]) -> str:
        """Generate document ID from metadata or use default."""
        if metadata and "document_id" in metadata:
            return str(metadata["document_id"])
        return str(uuid.uuid4())
