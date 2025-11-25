"""RAG Config service for managing workspace RAG configurations."""

from typing import Optional

from shared.models.workspace import RagConfig
from shared.repositories import RagConfigRepository


class RagConfigService:
    """Service for RAG configuration operations."""

    def __init__(self, repository: RagConfigRepository, workspace_service):
        """Initialize the service."""
        self.repository = repository
        self.workspace_service = workspace_service

    def get_rag_config(self, workspace_id: int, user_id: int) -> Optional[RagConfig]:
        """
        Get RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)

        Returns:
            RagConfig if found, None otherwise
        """
        # Validate workspace access
        if not self.workspace_service.validate_workspace_access(workspace_id, user_id):
            return None

        return self.repository.get_by_workspace_id(workspace_id)

    def create_rag_config(self, workspace_id: int, user_id: int, **config_data) -> RagConfig:
        """
        Create RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)
            **config_data: Configuration parameters

        Returns:
            Created RagConfig
        """
        # Validate workspace access
        if not self.workspace_service.validate_workspace_access(workspace_id, user_id):
            raise ValueError("No access to workspace")

        # Check if config already exists
        existing = self.repository.get_by_workspace_id(workspace_id)
        if existing:
            raise ValueError("RAG configuration already exists for this workspace")

        return self.repository.create(workspace_id, **config_data)

    def update_rag_config(self, workspace_id: int, user_id: int, **update_data) -> Optional[RagConfig]:
        """
        Update RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)
            **update_data: Fields to update

        Returns:
            Updated RagConfig if successful, None otherwise
        """
        # Validate workspace access
        if not self.workspace_service.validate_workspace_access(workspace_id, user_id):
            return None

        # Validate update data
        if update_data:
            self._validate_config_data(update_data)

        return self.repository.update(workspace_id, **update_data)

    def delete_rag_config(self, workspace_id: int, user_id: int) -> bool:
        """
        Delete RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)

        Returns:
            True if deleted, False otherwise
        """
        # Validate workspace access
        if not self.workspace_service.validate_workspace_access(workspace_id, user_id):
            return False

        return self.repository.delete(workspace_id)

    def _validate_config_data(self, config_data: dict) -> None:
        """
        Validate RAG configuration data.

        Args:
            config_data: Configuration data to validate

        Raises:
            ValueError: If validation fails
        """
        # Validate retriever_type
        if "retriever_type" in config_data:
            valid_types = ["vector", "graph", "hybrid"]
            if config_data["retriever_type"] not in valid_types:
                raise ValueError(f"retriever_type must be one of: {', '.join(valid_types)}")

        # Validate chunk_size
        if "chunk_size" in config_data:
            chunk_size = config_data["chunk_size"]
            if not (100 <= chunk_size <= 5000):
                raise ValueError("chunk_size must be between 100 and 5000")

        # Validate chunk_overlap
        if "chunk_overlap" in config_data:
            chunk_overlap = config_data["chunk_overlap"]
            if not (0 <= chunk_overlap <= 1000):
                raise ValueError("chunk_overlap must be between 0 and 1000")

        # Validate top_k
        if "top_k" in config_data:
            top_k = config_data["top_k"]
            if not (1 <= top_k <= 50):
                raise ValueError("top_k must be between 1 and 50")

        # Validate embedding_model (basic check)
        if "embedding_model" in config_data:
            model = config_data["embedding_model"]
            if not model or len(model.strip()) == 0:
                raise ValueError("embedding_model cannot be empty")