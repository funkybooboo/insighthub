"""Content retrieval from external sources."""

from shared.documents.retrieving.retriever import RetrievedContent, Retriever
from shared.documents.retrieving.retriever_registry import RetrieverRegistry, retriever_registry
from shared.documents.retrieving.url_retriever import URLRetriever
from shared.documents.retrieving.wikipedia_retriever import WikipediaRetriever

__all__ = [
    "Retriever",
    "RetrievedContent",
    "WikipediaRetriever",
    "URLRetriever",
    "RetrieverRegistry",
    "retriever_registry",
]
