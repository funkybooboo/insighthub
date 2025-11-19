"""Context builder interface for Vector RAG."""

from abc import ABC, abstractmethod
from typing import Any

from shared.types import RetrievalResult


class ContextBuilder(ABC):
    """
    Constructs LLM prompt from ranked chunks.

    Responsibilities:
    - Assemble textual context segments
    - Attach provenance for each snippet
    - Compress or summarize when token limits are exceeded
    """

    @abstractmethod
    def build(
        self,
        ranked_results: list[RetrievalResult],
        query: str | None = None,
        max_tokens: int | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """
        Build LLM context from retrieved chunks.

        Args:
            ranked_results: List of ranked RetrievalResult objects
            query: Original user query
            max_tokens: Optional maximum token limit

        Returns:
            Tuple of (prompt_text, metadata dictionary)
        """
        raise NotImplementedError
