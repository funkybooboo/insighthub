"""Factory for creating community detector instances.

This module provides a factory for creating community detection implementations
based on configuration.
"""

from typing import Optional

from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.graph_rag.clustering.base import CommunityDetector

logger = create_logger(__name__)


class CommunityDetectorFactory:
    """Factory for creating community detector instances."""

    @staticmethod
    def create(detector_type: str, **config) -> CommunityDetector:
        """Create a community detector instance.

        Args:
            detector_type: Type of detector ("leiden" or "louvain")
            **config: Configuration parameters for the detector

        Returns:
            CommunityDetector instance

        Raises:
            ValueError: If detector_type is not recognized

        Example:
            >>> # Leiden detector
            >>> detector = CommunityDetectorFactory.create(
            ...     "leiden",
            ...     resolution=1.0,
            ...     max_level=3,
            ...     llm_provider=my_llm_provider
            ... )
            >>>
            >>> # Louvain detector
            >>> detector = CommunityDetectorFactory.create(
            ...     "louvain",
            ...     resolution=1.0,
            ...     min_community_size=3
            ... )
        """
        if detector_type == "leiden":
            try:
                from src.infrastructure.rag.steps.graph_rag.clustering.leiden_detector import (
                    LeidenDetector,
                )
            except ImportError as e:
                raise ImportError(
                    "Leiden algorithm dependencies not installed. "
                    "Install with: pip install python-igraph leidenalg"
                ) from e

            resolution = config.get("resolution", 1.0)
            max_level = config.get("max_level", 3)
            min_community_size = config.get("min_size", 3)
            llm_provider: Optional[LlmProvider] = config.get("llm_provider")

            logger.info(f"Creating Leiden community detector with resolution={resolution}")
            return LeidenDetector(
                resolution=resolution,
                max_level=max_level,
                min_community_size=min_community_size,
                llm_provider=llm_provider,
            )

        elif detector_type == "louvain":
            try:
                from src.infrastructure.rag.steps.graph_rag.clustering.louvain_detector import (
                    LouvainDetector,
                )
            except ImportError as e:
                raise ImportError(
                    "Louvain algorithm dependencies not installed. "
                    "Install with: pip install networkx"
                ) from e

            resolution = config.get("resolution", 1.0)
            min_community_size = config.get("min_size", 3)
            louvain_llm_provider: Optional[LlmProvider] = config.get("llm_provider")

            logger.info(f"Creating Louvain community detector with resolution={resolution}")
            return LouvainDetector(
                resolution=resolution,
                min_community_size=min_community_size,
                llm_provider=louvain_llm_provider,
            )

        raise ValueError(f"Unknown community detector type: {detector_type}")

    @staticmethod
    def get_available_detectors() -> list[dict[str, str]]:
        """Get list of available community detectors.

        Returns:
            List of dictionaries with detector metadata
        """
        return [
            {
                "value": "leiden",
                "label": "Leiden Algorithm",
                "description": "Advanced community detection using the Leiden algorithm. Improved quality over Louvain. Requires python-igraph and leidenalg.",
            },
            {
                "value": "louvain",
                "label": "Louvain Algorithm",
                "description": "Fast community detection using the Louvain algorithm. Good for large graphs. Requires networkx.",
            },
        ]
