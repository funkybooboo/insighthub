"""Wikipedia infrastructure module."""

from .fetch import WikipediaArticle, WikipediaFetcher, wikipedia_fetcher

__all__ = ["WikipediaArticle", "WikipediaFetcher", "wikipedia_fetcher"]