"""Context building interface for constructing LLM prompts from retrieved chunks."""

from abc import ABC, abstractmethod
from typing import Any, List, Tuple

from shared.types.retrieval import RetrievalResult


class ContextBuilder(ABC):
    """
    Interface for building LLM context from retrieved chunks.
    
    Implementations should handle:
    - Prompt template formatting
    - Token limit management
    - Citation inclusion
    - Context compression
    """

    @abstractmethod
    def build(self, ranked_results: List[RetrievalResult], query: str | None = None, max_tokens: int | None = None) -> Tuple[str, dict[str, Any]]:
        """
        Build LLM context from ranked retrieval results.

        Args:
            ranked_results: List of ranked retrieval results
            query: Optional original query for context
            max_tokens: Optional maximum token limit

        Returns:
            Tuple[str, dict[str, Any]]: (prompt_text, context_metadata)

        Raises:
            ContextBuilderError: If context building fails
        """
        pass