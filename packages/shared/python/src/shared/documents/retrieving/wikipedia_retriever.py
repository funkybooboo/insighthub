"""Wikipedia content retriever implementation."""

import logging

import requests

from .retriever import RetrievedContent, Retriever

logger = logging.getLogger(__name__)


class WikipediaRetriever(Retriever):
    """
    Retrieves content from Wikipedia using the MediaWiki API.

    Example:
        retriever = WikipediaRetriever(language="en")
        results = retriever.retrieve("machine learning", max_results=5)
        for result in results:
            print(f"{result.source}: {result.content[:100]}...")
    """

    def __init__(
        self,
        language: str = "en",
        timeout: int = 30,
    ) -> None:
        """
        Initialize Wikipedia retriever.

        Args:
            language: Wikipedia language code (e.g., "en", "de", "fr")
            timeout: Request timeout in seconds
        """
        self.language = language
        self.timeout = timeout
        self.base_url = f"https://{language}.wikipedia.org/w/api.php"

    def retrieve(self, query: str, max_results: int = 5) -> list[RetrievedContent]:
        """
        Search Wikipedia and retrieve matching articles.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of retrieved Wikipedia articles
        """
        try:
            # Search for articles
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
            }

            response = requests.get(self.base_url, params=search_params, timeout=self.timeout)
            response.raise_for_status()
            search_data = response.json()

            search_results = search_data.get("query", {}).get("search", [])

            # Fetch content for each result
            results: list[RetrievedContent] = []
            for item in search_results:
                page_id = item.get("pageid")
                title = item.get("title", "")

                if page_id:
                    content = self._get_page_content(page_id)
                    if content:
                        results.append(
                            RetrievedContent(
                                source=f"wikipedia:{title}",
                                content=content,
                                metadata={
                                    "page_id": page_id,
                                    "title": title,
                                    "snippet": item.get("snippet", ""),
                                    "language": self.language,
                                    "url": f"https://{self.language}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                                },
                            )
                        )

            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []

    def retrieve_by_id(self, identifier: str) -> RetrievedContent | None:
        """
        Retrieve a Wikipedia article by title or page ID.

        Args:
            identifier: Wikipedia article title or page ID

        Returns:
            Retrieved article or None if not found
        """
        try:
            # Try to parse as page ID first
            if identifier.isdigit():
                params = {
                    "action": "query",
                    "pageids": identifier,
                    "prop": "extracts|info",
                    "explaintext": True,
                    "exsectionformat": "plain",
                    "inprop": "url",
                    "format": "json",
                }
            else:
                params = {
                    "action": "query",
                    "titles": identifier,
                    "prop": "extracts|info",
                    "explaintext": True,
                    "exsectionformat": "plain",
                    "inprop": "url",
                    "format": "json",
                }

            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})

            for page_id, page_data in pages.items():
                if page_id == "-1":  # Page not found
                    return None

                title = page_data.get("title", "")
                content = page_data.get("extract", "")
                url = page_data.get("fullurl", "")

                if content:
                    return RetrievedContent(
                        source=f"wikipedia:{title}",
                        content=content,
                        metadata={
                            "page_id": int(page_id),
                            "title": title,
                            "language": self.language,
                            "url": url,
                        },
                    )

            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Wikipedia retrieval failed: {e}")
            return None

    def get_source_name(self) -> str:
        """Get the source name."""
        return f"wikipedia-{self.language}"

    def _get_page_content(self, page_id: int) -> str | None:
        """
        Get the text content of a Wikipedia page.

        Args:
            page_id: Wikipedia page ID

        Returns:
            Page text content or None if failed
        """
        try:
            params = {
                "action": "query",
                "pageids": page_id,
                "prop": "extracts",
                "explaintext": True,
                "exsectionformat": "plain",
                "format": "json",
            }

            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            page_data = pages.get(str(page_id), {})

            return page_data.get("extract")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get page content for {page_id}: {e}")
            return None

    def get_random_articles(self, count: int = 5) -> list[RetrievedContent]:
        """
        Retrieve random Wikipedia articles.

        Args:
            count: Number of random articles to retrieve

        Returns:
            List of random articles
        """
        try:
            params = {
                "action": "query",
                "list": "random",
                "rnlimit": count,
                "rnnamespace": 0,  # Main namespace only
                "format": "json",
            }

            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            random_pages = data.get("query", {}).get("random", [])

            results: list[RetrievedContent] = []
            for page in random_pages:
                page_id = page.get("id")
                title = page.get("title", "")

                if page_id:
                    content = self._get_page_content(page_id)
                    if content:
                        results.append(
                            RetrievedContent(
                                source=f"wikipedia:{title}",
                                content=content,
                                metadata={
                                    "page_id": page_id,
                                    "title": title,
                                    "language": self.language,
                                    "url": f"https://{self.language}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                                },
                            )
                        )

            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get random articles: {e}")
            return []
