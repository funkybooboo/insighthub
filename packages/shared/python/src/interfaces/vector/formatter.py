"""Output formatter interface for Vector RAG."""

from abc import ABC, abstractmethod
from typing import Any


class OutputFormatter(ABC):
    """
    Formats raw LLM output for user consumption.

    Responsibilities:
    - Clean final text
    - Attach citations and provenance
    - Return structured JSON with answer, provenance, source list
    """

    @abstractmethod
    def format(
        self, raw_output: str, context_metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Format the LLM output into structured form.

        Args:
            raw_output: Raw text from LLM
            context_metadata: Optional metadata from context building

        Returns:
            Dictionary containing:
                'answer': str
                'provenance': list
                'raw': str
        """
        raise NotImplementedError
