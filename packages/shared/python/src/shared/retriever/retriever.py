"""Retriever interface for fetching content from various sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievedContent:
    """
    Content retrieved from an external source.

    Attributes:
        source: Source identifier (URL, Wikipedia title, etc.)
        content: Text content retrieved
        metadata: Additional metadata about the content
    """

    source: str
    content: str
    metadata: dict[str, Any]


class Retriever(ABC):
    """
    Abstract interface for content retrieval from external sources.

    Implementations should handle different content sources:
    - Wikipedia articles
    - Web URLs
    - Academic papers
    - Other external sources

    Example:
        retriever = WikipediaRetriever()
        results = retriever.retrieve("machine learning", max_results=5)
    """

    @abstractmethod
    def retrieve(
        self, query: str, max_results: int = 5
    ) -> list[RetrievedContent]:
        """
        Retrieve content matching the query.

        Args:
            query: Search query or identifier
            max_results: Maximum number of results to return

        Returns:
            List of retrieved content items
        """
        pass

    @abstractmethod
    def retrieve_by_id(self, identifier: str) -> RetrievedContent | None:
        """
        Retrieve specific content by identifier.

        Args:
            identifier: Unique identifier for the content

        Returns:
            Retrieved content or None if not found
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of this retriever's source.

        Returns:
            Source name string
        """
        pass
