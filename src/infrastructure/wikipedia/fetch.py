"""Wikipedia API client for fetching articles."""

import logging
import re
from typing import Dict, List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.infrastructure.types.result import Err, Ok, Result

logger = logging.getLogger(__name__)


class WikipediaFetchError(Exception):
    """Exception raised when Wikipedia fetch fails."""

    pass


class WikipediaArticle:
    """Represents a Wikipedia article with metadata and content."""

    def __init__(
        self,
        title: str,
        content: str,
        url: str,
        language: str,
        summary: Optional[str] = None,
        categories: Optional[List[str]] = None,
    ):
        self.title = title
        self.content = content
        self.url = url
        self.language = language
        self.summary = summary
        self.categories = categories or []

    def to_markdown(self) -> str:
        """Convert article to markdown format."""
        lines = [f"# {self.title}", ""]

        if self.summary:
            lines.extend([self.summary, ""])

        lines.extend(["---", f"**Source:** {self.url}", f"**Language:** {self.language}", ""])

        if self.categories:
            lines.extend([f"**Categories:** {', '.join(self.categories)}", ""])

        lines.extend(["---", "", self.content])

        return "\n".join(lines)


class WikipediaFetcher:
    """Client for fetching Wikipedia articles."""

    BASE_URL_TEMPLATE = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
    SEARCH_URL_TEMPLATE = "https://{lang}.wikipedia.org/w/api.php"

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def search_articles(
        self, query: str, language: str = "en", limit: int = 5
    ) -> Result[List[Dict[str, str]], str]:
        """
        Search for Wikipedia articles matching the query.

        Args:
            query: Search query
            language: Language code (e.g., 'en', 'es', 'fr')
            limit: Maximum number of results to return

        Returns:
            List of article summaries with title, url, and description
        """
        try:
            params = {
                "action": "opensearch",
                "search": query,
                "limit": limit,
                "namespace": 0,
                "format": "json",
            }

            url = self.SEARCH_URL_TEMPLATE.format(lang=language)
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            if len(data) < 4:
                return Err("Invalid search response format")

            titles = data[1]
            descriptions = data[2]
            urls = data[3]

            results = []
            for title, description, url in zip(titles, descriptions, urls):
                results.append(
                    {
                        "title": title,
                        "description": description,
                        "url": url,
                    }
                )

            return Ok(results)

        except requests.RequestException as e:
            logger.error(f"Wikipedia search failed for query '{query}': {e}")
            return Err(f"Search request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during Wikipedia search: {e}")
            return Err(f"Search failed: {str(e)}")

    def fetch_article(
        self, title_or_query: str, language: str = "en"
    ) -> Result[WikipediaArticle, str]:
        """
        Fetch a Wikipedia article by title or search for the best match.

        Args:
            title_or_query: Article title or search query
            language: Language code

        Returns:
            WikipediaArticle object or error message
        """
        # First try to fetch directly by title
        result = self._fetch_by_title(title_or_query, language)
        if result.is_ok():
            return result

        # If direct fetch fails, search and try the best match
        logger.info(f"Direct fetch failed for '{title_or_query}', trying search...")
        search_result = self.search_articles(title_or_query, language, limit=1)
        if search_result.is_err():
            return Err(f"Both direct fetch and search failed: {result.err()}")

        articles = search_result.unwrap()
        if not articles:
            return Err(f"No articles found for query: {title_or_query}")

        best_match = articles[0]
        best_title = best_match["title"]

        logger.info(f"Found best match: '{best_title}' for query '{title_or_query}'")
        return self._fetch_by_title(best_title, language)

    def _fetch_by_title(self, title: str, language: str = "en") -> Result[WikipediaArticle, str]:
        """Fetch article directly by title."""
        try:
            # URL encode the title
            encoded_title = quote(title.replace(" ", "_"))
            url = self.BASE_URL_TEMPLATE.format(lang=language, title=encoded_title)

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Check if article exists
            if "title" not in data:
                return Err(f"Article '{title}' not found")

            # Extract content
            title = data["title"]
            summary = data.get("extract", "")
            full_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

            # Try to get full HTML content for better parsing
            html_content = self._fetch_full_content(title, language)
            if html_content.is_ok():
                content = self._parse_html_content(html_content.unwrap())
            else:
                # Fallback to summary
                content = summary or "No content available"

            # Get categories if available
            categories = data.get("categories", [])
            category_names = [cat.get("title", "").replace("Category:", "") for cat in categories]

            article = WikipediaArticle(
                title=title,
                content=content,
                url=full_url,
                language=language,
                summary=summary,
                categories=category_names,
            )

            return Ok(article)

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return Err(f"Article '{title}' not found")
            return Err(f"HTTP error: {e.response.status_code}")
        except requests.RequestException as e:
            return Err(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching article '{title}': {e}")
            return Err(f"Failed to fetch article: {str(e)}")

    def _fetch_full_content(self, title: str, language: str) -> Result[str, str]:
        """Fetch full HTML content of the article."""
        try:
            encoded_title = quote(title.replace(" ", "_"))
            url = f"https://{language}.wikipedia.org/wiki/{encoded_title}"

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            return Ok(response.text)

        except requests.RequestException as e:
            return Err(f"Failed to fetch full content: {str(e)}")

    def _parse_html_content(self, html: str) -> str:
        """Parse HTML content and extract clean text."""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Find the main content
            content_div = soup.find("div", {"id": "mw-content-text"})
            if not content_div or not hasattr(content_div, "find_all"):
                return "Content parsing failed"

            # Remove unwanted elements
            for element in content_div.find_all(["table", "div", "span"], class_=["navbox", "vertical-navbox", "reflist", "mw-editsection"]):  # type: ignore
                element.decompose()

            # Extract text from paragraphs and headers
            text_parts = []

            for element in content_div.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"]):  # type: ignore
                text = element.get_text().strip()
                if text and hasattr(element, "name") and element.name:  # type: ignore
                    # Convert headers to markdown
                    if element.name.startswith("h"):  # type: ignore
                        level = int(element.name[1])  # type: ignore
                        text = "#" * level + " " + text
                    elif element.name == "li":  # type: ignore
                        text = "- " + text

                    text_parts.append(text)

            # Clean up the text
            content = "\n\n".join(text_parts)

            # Remove references like [1], [2], etc.
            content = re.sub(r"\[\d+\]", "", content)

            # Remove extra whitespace
            content = re.sub(r"\n{3,}", "\n\n", content)

            return content.strip()

        except Exception as e:
            logger.error(f"Failed to parse HTML content: {e}")
            return "Content parsing failed"


# Global instance for reuse
wikipedia_fetcher = WikipediaFetcher()
