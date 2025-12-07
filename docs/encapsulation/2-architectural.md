# Architectural Encapsulation Opportunities (TIER 2)

**Impact**: Cleaner architecture for RAG type polymorphism
**RAG Compatibility**: Key pattern for handling both Vector and Graph RAG

---

## 1. RAG Config Provider Abstraction

**Problem**: Conditional branches for Vector vs Graph RAG config scattered throughout services.

**Current Code**:
```python
# In multiple services - repeated conditional logic
if workspace.rag_type == "vector":
    config = self.vector_config_data_access.get_by_workspace_id(workspace_id)
    if config:
        rag_config = {
            "rag_type": "vector",
            "embedding_algorithm": config.embedding_algorithm,
            "chunk_size": config.chunk_size,
            # ... 20+ more fields
        }
elif workspace.rag_type == "graph":
    config = self.graph_config_data_access.get_by_workspace_id(workspace_id)
    if config:
        rag_config = {
            "rag_type": "graph",
            "llm_provider": config.llm_provider,
            "enable_community_reports": config.enable_community_reports,
            # ... 15+ more fields
        }
else:
    raise ValueError(f"Unknown RAG type: {workspace.rag_type}")
```

**Solution**:
```python
from abc import ABC, abstractmethod
from typing import Optional, Any

class RagConfigProvider(ABC):
    """Abstract provider for RAG configuration."""

    @abstractmethod
    def get_config_model(self, workspace_id: int) -> Optional[Any]:
        """Get RAG config model for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Config model or None if not found
        """
        pass

    @abstractmethod
    def build_query_settings(self, workspace_id: int) -> Optional[dict]:
        """Build query workflow settings for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Query settings dict or None if no config
        """
        pass

    @abstractmethod
    def build_indexing_settings(self, workspace_id: int) -> Optional[dict]:
        """Build indexing workflow settings for workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Indexing settings dict or None if no config
        """
        pass


class VectorRagConfigProvider(RagConfigProvider):
    """Provider for Vector RAG configuration."""

    def __init__(
        self,
        config_data_access: VectorRagConfigDataAccess,
        storage_manager: StorageManager,
        vector_store_factory: VectorStoreFactory
    ):
        self.config_data_access = config_data_access
        self.storage_manager = storage_manager
        self.vector_store_factory = vector_store_factory

    def get_config_model(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get vector RAG config."""
        return self.config_data_access.get_by_workspace_id(workspace_id)

    def build_query_settings(self, workspace_id: int) -> Optional[dict]:
        """Build vector query settings."""
        config = self.get_config_model(workspace_id)
        if not config:
            return None

        return {
            "rag_type": "vector",
            "embedding_algorithm": config.embedding_algorithm,
            "embedding_model": config.embedding_model,
            "reranking_algorithm": config.reranking_algorithm,
            "reranking_model": config.reranking_model,
            "retrieval_k": config.retrieval_k,
            "similarity_threshold": config.similarity_threshold,
            "vector_store": self.vector_store_factory.create(config),
        }

    def build_indexing_settings(self, workspace_id: int) -> Optional[dict]:
        """Build vector indexing settings."""
        config = self.get_config_model(workspace_id)
        if not config:
            return None

        return {
            "rag_type": "vector",
            "chunking_algorithm": config.chunking_algorithm,
            "chunk_size": config.chunk_size,
            "chunk_overlap": config.chunk_overlap,
            "embedding_algorithm": config.embedding_algorithm,
            "embedding_model": config.embedding_model,
            "vector_store": self.vector_store_factory.create(config),
            "storage": self.storage_manager.get_storage(),
        }


class GraphRagConfigProvider(RagConfigProvider):
    """Provider for Graph RAG configuration."""

    def __init__(
        self,
        config_data_access: GraphRagConfigDataAccess,
        llm_provider_factory: LlmProviderFactory
    ):
        self.config_data_access = config_data_access
        self.llm_provider_factory = llm_provider_factory

    def get_config_model(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config."""
        return self.config_data_access.get_by_workspace_id(workspace_id)

    def build_query_settings(self, workspace_id: int) -> Optional[dict]:
        """Build graph query settings."""
        config = self.get_config_model(workspace_id)
        if not config:
            return None

        return {
            "rag_type": "graph",
            "llm_provider": self.llm_provider_factory.create(config.llm_provider),
            "community_level": config.community_level,
            "use_community_reports": config.enable_community_reports,
        }

    def build_indexing_settings(self, workspace_id: int) -> Optional[dict]:
        """Build graph indexing settings."""
        config = self.get_config_model(workspace_id)
        if not config:
            return None

        return {
            "rag_type": "graph",
            "llm_provider": self.llm_provider_factory.create(config.llm_provider),
            "enable_community_reports": config.enable_community_reports,
            "max_graph_tokens": config.max_graph_tokens,
        }


# Factory to get the right provider
class RagConfigProviderFactory:
    """Factory for creating RAG config providers."""

    def __init__(
        self,
        vector_provider: VectorRagConfigProvider,
        graph_provider: GraphRagConfigProvider
    ):
        self._providers = {
            "vector": vector_provider,
            "graph": graph_provider,
        }

    def get_provider(self, rag_type: str) -> Optional[RagConfigProvider]:
        """Get config provider for RAG type.

        Args:
            rag_type: Either "vector" or "graph"

        Returns:
            Appropriate config provider or None if unknown RAG type
        """
        return self._providers.get(rag_type)


# Usage in services - clean polymorphism with errors as values
class MessageService:
    def __init__(self, config_provider_factory: RagConfigProviderFactory, ...):
        self.config_provider_factory = config_provider_factory

    def send_message(
        self,
        workspace_id: int,
        message: str
    ) -> Result[MessageResponse, ServiceError]:
        workspace = self.workspace_service.get_by_id(workspace_id)

        # No more conditionals - polymorphism handles it
        provider = self.config_provider_factory.get_provider(workspace.rag_type)
        if not provider:
            return Failure(ServiceError(
                message=f"Unknown RAG type: {workspace.rag_type}",
                operation="send_message"
            ))

        query_settings = provider.build_query_settings(workspace_id)
        if not query_settings:
            return Failure(ServiceError(
                message="No RAG config found for workspace",
                operation="send_message"
            ))

        # Query settings dict has everything needed, type-specific
        result = self.query_workflow.execute(message, query_settings)
        return result
```

**Locations**:
- `src/domains/workspace/service.py:121-175` - workspace provisioning
- `src/domains/workspace/chat/message/service.py:207-262` - message handling
- `src/domains/workspace/document/service.py` - document processing

**Why Valuable**:
- **Eliminates all conditional "if vector else graph" logic**
- Services work with abstraction, don't know about specific RAG types
- Easy to add new RAG types (just implement interface)
- Config building logic centralized per RAG type
- Type-specific dependencies encapsulated in providers
- Makes services simpler and focused on business logic

**Implementation Notes**:
- Start with VectorRagConfigProvider (most common)
- Migrate existing vector config logic into provider
- Add GraphRagConfigProvider with same interface
- Update services to use factory pattern
- Remove all conditional RAG type checks from services
