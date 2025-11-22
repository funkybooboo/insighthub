"""Registry for managing multiple retrievers."""

from .retriever import RetrievedContent, Retriever


class RetrieverRegistry:
    """
    Registry for managing multiple content retrievers.

    Provides a unified interface to search across multiple content sources
    and aggregate results.

    Example:
        registry = RetrieverRegistry()
        registry.register(WikipediaRetriever())
        registry.register(URLRetriever())

        # Search all registered retrievers
        results = registry.retrieve_all("machine learning", max_results_per_source=3)
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._retrievers: dict[str, Retriever] = {}

    def register(self, retriever: Retriever, name: str | None = None) -> None:
        """
        Register a retriever.

        Args:
            retriever: Retriever instance to register
            name: Optional custom name (defaults to retriever's source name)
        """
        key = name or retriever.get_source_name()
        self._retrievers[key] = retriever

    def unregister(self, name: str) -> bool:
        """
        Unregister a retriever.

        Args:
            name: Name of the retriever to unregister

        Returns:
            True if removed, False if not found
        """
        if name in self._retrievers:
            del self._retrievers[name]
            return True
        return False

    def get(self, name: str) -> Retriever | None:
        """
        Get a retriever by name.

        Args:
            name: Retriever name

        Returns:
            Retriever instance or None if not found
        """
        return self._retrievers.get(name)

    def list_retrievers(self) -> list[str]:
        """
        List all registered retriever names.

        Returns:
            List of retriever names
        """
        return list(self._retrievers.keys())

    def retrieve(self, source: str, query: str, max_results: int = 5) -> list[RetrievedContent]:
        """
        Retrieve content from a specific source.

        Args:
            source: Retriever name
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of retrieved content

        Raises:
            KeyError: If source not found
        """
        retriever = self._retrievers.get(source)
        if not retriever:
            raise KeyError(f"Retriever not found: {source}")

        return retriever.retrieve(query, max_results)

    def retrieve_all(
        self,
        query: str,
        max_results_per_source: int = 5,
        sources: list[str] | None = None,
    ) -> dict[str, list[RetrievedContent]]:
        """
        Retrieve content from all (or specified) sources.

        Args:
            query: Search query
            max_results_per_source: Maximum results per source
            sources: Optional list of source names to search

        Returns:
            Dictionary mapping source names to results
        """
        target_sources = sources or list(self._retrievers.keys())
        results: dict[str, list[RetrievedContent]] = {}

        for source in target_sources:
            retriever = self._retrievers.get(source)
            if retriever:
                try:
                    source_results = retriever.retrieve(query, max_results_per_source)
                    results[source] = source_results
                except Exception:
                    # Log error but continue with other sources
                    results[source] = []

        return results

    def retrieve_merged(
        self,
        query: str,
        max_results_per_source: int = 5,
        sources: list[str] | None = None,
    ) -> list[RetrievedContent]:
        """
        Retrieve and merge content from multiple sources.

        Args:
            query: Search query
            max_results_per_source: Maximum results per source
            sources: Optional list of source names to search

        Returns:
            Merged list of all results
        """
        all_results = self.retrieve_all(query, max_results_per_source, sources)

        merged: list[RetrievedContent] = []
        for source_results in all_results.values():
            merged.extend(source_results)

        return merged

    def retrieve_by_id(self, source: str, identifier: str) -> RetrievedContent | None:
        """
        Retrieve specific content by identifier from a source.

        Args:
            source: Retriever name
            identifier: Content identifier

        Returns:
            Retrieved content or None

        Raises:
            KeyError: If source not found
        """
        retriever = self._retrievers.get(source)
        if not retriever:
            raise KeyError(f"Retriever not found: {source}")

        return retriever.retrieve_by_id(identifier)

    def __len__(self) -> int:
        """Return number of registered retrievers."""
        return len(self._retrievers)

    def __contains__(self, name: str) -> bool:
        """Check if a retriever is registered."""
        return name in self._retrievers


# Global registry instance
retriever_registry = RetrieverRegistry()
