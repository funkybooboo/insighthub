"""URL content retriever implementation."""

import logging
import re
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests

from shared.types.common import MetadataDict

from .retriever import RetrievedContent, Retriever

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None


class URLRetriever(Retriever):
    """
    Retrieves and extracts content from web URLs.

    Fetches web pages and extracts text content using BeautifulSoup.
    Supports cleaning and normalizing HTML content.

    Example:
        retriever = URLRetriever()
        result = retriever.retrieve_by_id("https://example.com/article")
        if result:
            print(result.content)
    """

    def __init__(
        self,
        timeout: int = 30,
        user_agent: str | None = None,
        max_content_length: int = 1_000_000,
    ) -> None:
        """
        Initialize URL retriever.

        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
            max_content_length: Maximum content length to fetch (bytes)
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = user_agent or (
            "Mozilla/5.0 (compatible; InsightHub/1.0; +https://insighthub.example.com)"
        )

    def retrieve(self, query: str, max_results: int = 5) -> list[RetrievedContent]:
        """
        Retrieve content from URLs.

        Note: This method treats the query as a URL if it looks like one,
        otherwise returns empty list. For search functionality, use a
        search engine API.

        Args:
            query: URL or search query
            max_results: Maximum number of results (not used for URLs)

        Returns:
            List containing the retrieved URL content
        """
        # Check if query looks like a URL
        if self._is_url(query):
            result = self.retrieve_by_id(query)
            return [result] if result else []

        # Not a URL - return empty list
        logger.warning(f"Query is not a URL: {query}")
        return []

    def retrieve_by_id(self, identifier: str) -> RetrievedContent | None:
        """
        Retrieve content from a specific URL.

        Args:
            identifier: The URL to fetch

        Returns:
            Retrieved content or None if failed
        """
        if not self._is_url(identifier):
            logger.error(f"Invalid URL: {identifier}")
            return None

        if not BS4_AVAILABLE:
            logger.error("BeautifulSoup not available for HTML parsing")
            return None

        try:
            headers = {"User-Agent": self.user_agent}

            response = requests.get(identifier, headers=headers, timeout=self.timeout, stream=True)
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_content_length:
                logger.warning(f"Content too large: {content_length} bytes")
                return None

            # Check content type
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                logger.warning(f"Unsupported content type: {content_type}")
                return None

            # Read content with size limit
            content = response.content[: self.max_content_length]
            html_text = self._decode_content(content)

            # Parse and extract text
            soup = BeautifulSoup(html_text, "html.parser")
            text_content = self._extract_text(soup)
            metadata = self._extract_metadata(soup, identifier, response)

            return RetrievedContent(
                source=f"url:{identifier}",
                content=text_content,
                metadata=metadata,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch URL {identifier}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing URL {identifier}: {e}")
            return None

    def get_source_name(self) -> str:
        """Get the source name."""
        return "url"

    def _is_url(self, text: str) -> bool:
        """Check if text is a valid URL."""
        try:
            result = urlparse(text)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    def _decode_content(self, content: bytes) -> str:
        """Decode content with fallback encodings."""
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        return content.decode("utf-8", errors="replace")

    def _extract_text(self, soup: "BeautifulSoup") -> str:
        """
        Extract clean text content from parsed HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Cleaned text content
        """
        # Remove script and style elements
        for element in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            element.decompose()

        # Get text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        return text.strip()

    def _extract_metadata(
        self, soup: "BeautifulSoup", url: str, response: requests.Response
    ) -> MetadataDict:
        """
        Extract metadata from the page.

        Args:
            soup: BeautifulSoup object
            url: Original URL
            response: HTTP response object

        Returns:
            Metadata dictionary
        """
        metadata: MetadataDict = {
            "url": url,
            "domain": urlparse(url).netloc,
            "status_code": response.status_code,
        }

        # Extract title
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            metadata["title"] = title_tag.string.strip()

        # Extract meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            content = meta.get("content", "")

            if name and content:
                if name == "description":
                    metadata["description"] = content
                elif name == "keywords":
                    metadata["keywords"] = content
                elif name == "author":
                    metadata["author"] = content

            # Open Graph metadata
            property_name = meta.get("property", "").lower()
            if property_name and content:
                if property_name == "og:title":
                    metadata["og_title"] = content
                elif property_name == "og:description":
                    metadata["og_description"] = content

        # Content info
        content_type = response.headers.get("content-type", "")
        metadata["content_type"] = content_type

        return metadata

    def retrieve_multiple(self, urls: list[str]) -> list[RetrievedContent]:
        """
        Retrieve content from multiple URLs.

        Args:
            urls: List of URLs to fetch

        Returns:
            List of successfully retrieved content
        """
        results: list[RetrievedContent] = []

        for url in urls:
            result = self.retrieve_by_id(url)
            if result:
                results.append(result)

        return results
