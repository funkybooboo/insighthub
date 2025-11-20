"""Output formatting interface for structuring LLM responses with citations."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class OutputFormatter(ABC):
    """
    Interface for formatting raw LLM output into user-facing responses.
    
    Implementations should handle:
    - Answer formatting
    - Citation inclusion
    - Metadata attachment
    - Error handling
    """

    @abstractmethod
    def format(self, raw_output: str, context_metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Format raw LLM output into a structured response.

        Args:
            raw_output: Raw text from LLM
            context_metadata: Optional metadata from context building

        Returns:
            Dict[str, Any]: Formatted response with keys:
                - 'answer': str (formatted answer)
                - 'provenance': list (source citations)
                - 'raw': str (original LLM output)
                - 'metadata': dict (additional metadata)

        Raises:
            FormattingError: If formatting fails
        """
        pass