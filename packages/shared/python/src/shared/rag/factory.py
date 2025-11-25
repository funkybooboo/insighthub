"""Factory for creating RAG systems and their components."""

import importlib
from typing import Any, Dict, Optional, Type

from shared.config import Config
from shared.rag.base import RAGConfig, RAGSystem, WorkerFactory


class RAGSystemFactory:
    """
    Factory for creating RAG systems based on configuration.

    Supports dynamic loading of RAG system implementations and
    provides a unified interface for creating different types of RAG systems.
    """

    _system_registry: Dict[str, Type[RAGSystem]] = {}
    _worker_factory_registry: Dict[str, Type[WorkerFactory]] = {}

    @classmethod
    def register_system(cls, system_type: str, system_class: Type[RAGSystem]) -> None:
        """
        Register a RAG system implementation.

        Args:
            system_type: Type identifier for the system
            system_class: The RAG system class
        """
        cls._system_registry[system_type] = system_class

    @classmethod
    def register_worker_factory(cls, system_type: str, factory_class: Type[WorkerFactory]) -> None:
        """
        Register a worker factory for a RAG system type.

        Args:
            system_type: Type identifier for the system
            factory_class: The worker factory class
        """
        cls._worker_factory_registry[system_type] = factory_class

    @classmethod
    def create_system(cls, config: RAGConfig) -> RAGSystem:
        """
        Create a RAG system instance based on configuration.

        Args:
            config: RAG system configuration

        Returns:
            Configured RAG system instance

        Raises:
            ValueError: If system type is not registered
        """
        system_type = config.system_type

        if system_type not in cls._system_registry:
            raise ValueError(f"RAG system type '{system_type}' is not registered")

        system_class = cls._system_registry[system_type]
        return system_class(config)

    @classmethod
    def create_worker_factory(cls, system_type: str) -> WorkerFactory:
        """
        Create a worker factory for a RAG system type.

        Args:
            system_type: Type identifier for the system

        Returns:
            Worker factory instance

        Raises:
            ValueError: If system type is not registered
        """
        if system_type not in cls._worker_factory_registry:
            raise ValueError(f"Worker factory for system type '{system_type}' is not registered")

        factory_class = cls._worker_factory_registry[system_type]
        return factory_class()

    @classmethod
    def load_from_config(cls, config: Config) -> Optional[RAGSystem]:
        """
        Load and create a RAG system from application configuration.

        Args:
            config: Application configuration

        Returns:
            RAG system instance or None if not configured
        """
        # This would read from config to determine which RAG system to create
        # For now, return None as this needs to be implemented based on config structure
        return None

    @classmethod
    def discover_systems(cls) -> Dict[str, Type[RAGSystem]]:
        """
        Discover available RAG systems.

        Returns:
            Dictionary mapping system types to system classes
        """
        return cls._system_registry.copy()


def create_rag_system(system_type: str, **config_kwargs) -> RAGSystem:
    """
    Convenience function to create a RAG system.

    Args:
        system_type: Type of RAG system to create
        **config_kwargs: Configuration parameters

    Returns:
        RAG system instance
    """
    # Create a basic config object - in practice this would be more sophisticated
    config = BasicRAGConfig(system_type, config_kwargs)
    return RAGSystemFactory.create_system(config)


class BasicRAGConfig:
    """Basic implementation of RAGConfig for simple use cases."""

    def __init__(self, system_type: str, components: Dict[str, Any]):
        self._system_type = system_type
        self._components = components

    @property
    def system_type(self) -> str:
        return self._system_type

    @property
    def components(self) -> Dict[str, Any]:
        return self._components.copy()

    def validate(self) -> bool:
        """Basic validation - always returns True for now."""
        return True


# Auto-register built-in RAG systems
def _register_builtin_systems():
    """Register the built-in RAG systems."""
    try:
        # Import and register Vector RAG
        from shared.orchestrators.vector_rag import VectorRAG
        RAGSystemFactory.register_system("vector", VectorRAG)

        # Import and register Graph RAG
        from shared.orchestrators.graph_rag import GraphRAG
        RAGSystemFactory.register_system("graph", GraphRAG)

        # Register worker factories (to be implemented)
        # RAGSystemFactory.register_worker_factory("vector", VectorWorkerFactory)
        # RAGSystemFactory.register_worker_factory("graph", GraphWorkerFactory)

    except ImportError as e:
        # Systems may not be fully implemented yet
        pass


# Register built-in systems on module load
_register_builtin_systems()