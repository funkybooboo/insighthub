"""Factory for creating retriever instances."""

from enum import Enum
from typing import Optional

from .retriever import Retriever
from .url_retriever import URLRetriever
from .wikipedia_retriever import WikipediaRetriever


class RetrieverType(Enum):
    """Enum for retriever implementation types."""

    WIKIPEDIA = "wikipedia"
    URL = "url"


def create_retriever(
    retriever_type: str,
    language: str = "en",
    timeout: int = 10,
    user_agent: str | None = None,
) -> Optional[Retriever]:
    """
    Create a retriever instance based on configuration.

    Args:
        retriever_type: Type of retriever ("wikipedia", "url")
        language: Wikipedia language code (default "en", only for wikipedia)
        timeout: Request timeout in seconds (default 10)
        user_agent: Custom user agent string (optional)

    Returns:
        Retriever if creation succeeds, None if type unknown

    Note:
        Additional retriever types can be added here when implemented.
    """
    try:
        retriever_enum = RetrieverType(retriever_type)
    except ValueError:
        return None

    if retriever_enum == RetrieverType.WIKIPEDIA:
        return WikipediaRetriever(
            language=language,
            timeout=timeout,
        )
    elif retriever_enum == RetrieverType.URL:
        return URLRetriever(
            timeout=timeout,
            user_agent=user_agent,
        )

    return None
