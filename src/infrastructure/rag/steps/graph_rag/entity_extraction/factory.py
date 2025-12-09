"""Factory for creating entity extractor instances.

This module provides a factory for creating entity extraction implementations
based on configuration.
"""

from typing import Optional

from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.entity_extraction.entity_extractor import (
    EntityExtractor,
)
from src.infrastructure.rag.steps.graph_rag.entity_extraction.llm_entity_extractor import (
    LlmEntityExtractor,
)
from src.infrastructure.types.graph import EntityType

logger = create_logger(__name__)


class EntityExtractorFactory:
    """Factory for creating entity extractor instances."""

    @staticmethod
    def create(extractor_type: str, **config) -> EntityExtractor:
        """Create an entity extractor instance.

        Args:
            extractor_type: Type of extractor ("spacy" or "llm")
            **config: Configuration parameters for the extractor

        Returns:
            EntityExtractor instance

        Raises:
            ValueError: If extractor_type is not recognized

        Example:
            >>> # SpaCy extractor
            >>> extractor = EntityExtractorFactory.create(
            ...     "spacy",
            ...     model="en_core_web_sm",
            ...     entity_types=[EntityType.PERSON, EntityType.ORGANIZATION]
            ... )
            >>>
            >>> # LLM extractor
            >>> extractor = EntityExtractorFactory.create(
            ...     "llm",
            ...     llm_provider=my_llm_provider,
            ...     temperature=0.1
            ... )
        """
        if extractor_type == "spacy":
            try:
                from src.infrastructure.rag.steps.graph_rag.entity_extraction.spacy_entity_extractor import (
                    SpacyEntityExtractor,
                )
            except ImportError as e:
                raise ImportError(
                    "spaCy dependencies not installed. "
                    "Install with: pip install spacy && python -m spacy download en_core_web_sm"
                ) from e

            model_name = config.get("model", "en_core_web_sm")
            entity_types = config.get("entity_types")
            min_confidence = config.get("min_confidence", 0.5)

            # Convert string entity types to EntityType enums if needed
            if entity_types and isinstance(entity_types[0], str):
                entity_types = [EntityType(et) for et in entity_types]

            logger.info(f"Creating SpaCy entity extractor with model: {model_name}")
            return SpacyEntityExtractor(
                model_name=model_name,
                entity_types=entity_types,
                min_confidence=min_confidence,
            )

        elif extractor_type == "llm":
            llm_provider: Optional[LlmProvider] = config.get("llm_provider")
            if not llm_provider:
                raise ValueError("llm_provider is required for LLM entity extractor")

            entity_types = config.get("entity_types")
            temperature = config.get("temperature", 0.1)
            max_retries = config.get("max_retries", 3)

            # Convert string entity types to EntityType enums if needed
            if entity_types and isinstance(entity_types[0], str):
                entity_types = [EntityType(et) for et in entity_types]

            logger.info("Creating LLM entity extractor")
            return LlmEntityExtractor(
                llm_provider=llm_provider,
                entity_types=entity_types,
                temperature=temperature,
                max_retries=max_retries,
            )

        raise ValueError(f"Unknown entity extractor type: {extractor_type}")

    @staticmethod
    def get_available_extractors() -> list[dict[str, str]]:
        """Get list of available entity extractors.

        Returns:
            List of dictionaries with extractor metadata
        """
        return [
            {
                "value": "spacy",
                "label": "spaCy NER",
                "description": "Fast and accurate named entity recognition using spaCy's transformer models. Supports offline operation.",
            },
            {
                "value": "llm",
                "label": "LLM-based Extraction",
                "description": "Flexible entity extraction using large language models with structured JSON output. Requires LLM provider.",
            },
        ]
