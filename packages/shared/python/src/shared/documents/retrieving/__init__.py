"""Content retrieval from external sources."""

from shared.retriever.retriever import Retriever, RetrievedContent
from shared.retriever.wikipedia_retriever import WikipediaRetriever
from shared.retriever.url_retriever import URLRetriever
from shared.retriever.retriever_registry import RetrieverRegistry, retriever_registry

__all__ = [
    "Retriever",
    "RetrievedContent",
    "WikipediaRetriever",
    "URLRetriever",
    "RetrieverRegistry",
    "retriever_registry",
]
