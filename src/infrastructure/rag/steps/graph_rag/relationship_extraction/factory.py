"""Factory for creating relationship extractor instances.

This module provides a factory for creating relationship extraction implementations
based on configuration.
"""

from typing import Optional

from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.relationship_extraction.base import (
    RelationshipExtractor,
)
from src.infrastructure.rag.steps.graph_rag.relationship_extraction.llm_relationship_extractor import (
    LlmRelationshipExtractor,
)
from src.infrastructure.types.graph import RelationType

logger = create_logger(__name__)


class RelationshipExtractorFactory:
    """Factory for creating relationship extractor instances."""

    @staticmethod
    def create(extractor_type: str, **config) -> RelationshipExtractor:
        """Create a relationship extractor instance.

        Args:
            extractor_type: Type of extractor ("dependency-parsing" or "llm")
            **config: Configuration parameters for the extractor

        Returns:
            RelationshipExtractor instance

        Raises:
            ValueError: If extractor_type is not recognized

        Example:
            >>> # Dependency parser extractor
            >>> extractor = RelationshipExtractorFactory.create(
            ...     "dependency-parsing",
            ...     model="en_core_web_sm",
            ...     relationship_types=[RelationType.WORKS_AT, RelationType.LOCATED_IN]
            ... )
            >>>
            >>> # LLM extractor
            >>> extractor = RelationshipExtractorFactory.create(
            ...     "llm",
            ...     llm_provider=my_llm_provider,
            ...     temperature=0.1
            ... )
        """
        if extractor_type == "dependency-parsing":
            try:
                from src.infrastructure.rag.steps.graph_rag.relationship_extraction.dependency_parser_extractor import (
                    DependencyParserExtractor,
                )
            except ImportError as e:
                raise ImportError(
                    "spaCy dependencies not installed. "
                    "Install with: pip install spacy && python -m spacy download en_core_web_sm"
                ) from e

            model_name = config.get("model", "en_core_web_sm")
            relationship_types = config.get("relationship_types")
            min_confidence = config.get("min_confidence", 0.6)

            # Convert string relationship types to RelationType enums if needed
            if relationship_types and isinstance(relationship_types[0], str):
                relationship_types = [RelationType(rt) for rt in relationship_types]

            logger.info(
                f"Creating dependency parser relationship extractor with model: {model_name}"
            )
            return DependencyParserExtractor(
                model_name=model_name,
                relationship_types=relationship_types,
                min_confidence=min_confidence,
            )

        elif extractor_type == "llm":
            llm_provider: Optional[LlmProvider] = config.get("llm_provider")
            if not llm_provider:
                raise ValueError("llm_provider is required for LLM relationship extractor")

            relationship_types = config.get("relationship_types")
            temperature = config.get("temperature", 0.1)
            max_retries = config.get("max_retries", 3)

            # Convert string relationship types to RelationType enums if needed
            if relationship_types and isinstance(relationship_types[0], str):
                relationship_types = [RelationType(rt) for rt in relationship_types]

            logger.info("Creating LLM relationship extractor")
            return LlmRelationshipExtractor(
                llm_provider=llm_provider,
                relationship_types=relationship_types,
                temperature=temperature,
                max_retries=max_retries,
            )

        raise ValueError(f"Unknown relationship extractor type: {extractor_type}")

    @staticmethod
    def get_available_extractors() -> list[dict[str, str]]:
        """Get list of available relationship extractors.

        Returns:
            List of dictionaries with extractor metadata
        """
        return [
            {
                "value": "dependency-parsing",
                "label": "Dependency Parsing",
                "description": "Extract relationships using spaCy's dependency parser to identify subject-verb-object triples. Fast and accurate for well-structured text.",
            },
            {
                "value": "llm",
                "label": "LLM-based Extraction",
                "description": "Flexible relationship extraction using large language models with structured JSON output. Better for complex relationships. Requires LLM provider.",
            },
        ]
