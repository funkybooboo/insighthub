"""Vector RAG configuration service."""

from typing import Optional

from shared.repositories.vector_rag_config.vector_rag_config_repository import VectorRagConfigRepository
from shared.repositories.workspace.workspace_repository import WorkspaceRepository
from shared.types.rag import VectorRagConfig


class VectorRagConfigService:
    """Service for Vector RAG configuration operations."""

    def __init__(self, repository: VectorRagConfigRepository, workspace_repository: WorkspaceRepository):
        """Initialize the service."""
        self.repository = repository
        self.workspace_repository = workspace_repository

    def _validate_workspace_access(self, workspace_id: int, user_id: int) -> bool:
        """Validate that user has access to the workspace."""
        workspace = self.workspace_repository.get_by_id(workspace_id)
        return workspace is not None and workspace.user_id == user_id

    def get_vector_rag_config(self, workspace_id: int, user_id: int) -> Optional[VectorRagConfig]:
        """
        Get Vector RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID

        Returns:
            VectorRagConfig if found, None otherwise
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            return None
        return self.repository.get_vector_rag_config(workspace_id)

    def create_vector_rag_config(
        self,
        workspace_id: int,
        user_id: int,
        embedding_algorithm: str = "nomic-embed-text",
        chunking_algorithm: str = "sentence",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 8,
        rerank_enabled: bool = False,
        rerank_algorithm: Optional[str] = None,
    ) -> VectorRagConfig:
        """
        Create Vector RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)
            embedding_algorithm: The embedding algorithm to use
            chunking_algorithm: The chunking algorithm to use
            chunk_size: The chunk size for text splitting
            chunk_overlap: The chunk overlap for text splitting
            top_k: The number of top results to retrieve
            rerank_enabled: Whether reranking is enabled
            rerank_algorithm: The reranking algorithm (optional)

        Returns:
            Created VectorRagConfig

        Raises:
            ValueError: If validation fails
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            raise ValueError("User does not have access to this workspace")

        self._validate_vector_config(
            embedding_algorithm=embedding_algorithm,
            chunking_algorithm=chunking_algorithm,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
            rerank_algorithm=rerank_algorithm,
        )

        # Check if config already exists
        existing = self.repository.get_vector_rag_config(workspace_id)
        if existing:
            raise ValueError("Vector RAG configuration already exists for this workspace")

        return self.repository.create_vector_rag_config(
            workspace_id=workspace_id,
            embedding_algorithm=embedding_algorithm,
            chunking_algorithm=chunking_algorithm,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
            rerank_enabled=rerank_enabled,
            rerank_algorithm=rerank_algorithm,
        )

    def update_vector_rag_config(
        self,
        workspace_id: int,
        user_id: int,
        embedding_algorithm: Optional[str] = None,
        chunking_algorithm: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        top_k: Optional[int] = None,
        rerank_enabled: Optional[bool] = None,
        rerank_algorithm: Optional[str] = None,
    ) -> Optional[VectorRagConfig]:
        """
        Update Vector RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)
            embedding_algorithm: The embedding algorithm to use
            chunking_algorithm: The chunking algorithm to use
            chunk_size: The chunk size
            chunk_overlap: The chunk overlap
            top_k: The number of top results
            rerank_enabled: Whether reranking is enabled
            rerank_algorithm: The reranking algorithm

        Returns:
            Updated VectorRagConfig if successful, None otherwise

        Raises:
            ValueError: If validation fails
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            return None

        if any([
            embedding_algorithm, chunking_algorithm, chunk_size,
            chunk_overlap, top_k, rerank_enabled, rerank_algorithm
        ]):
            # Get current config for validation
            current = self.repository.get_vector_rag_config(workspace_id)
            if current:
                self._validate_vector_config(
                    embedding_algorithm=embedding_algorithm or current.embedding_algorithm,
                    chunking_algorithm=chunking_algorithm or current.chunking_algorithm,
                    chunk_size=chunk_size if chunk_size is not None else current.chunk_size,
                    chunk_overlap=chunk_overlap if chunk_overlap is not None else current.chunk_overlap,
                    top_k=top_k if top_k is not None else current.top_k,
                    rerank_algorithm=rerank_algorithm,
                )

        return self.repository.update_vector_rag_config(
            workspace_id=workspace_id,
            embedding_algorithm=embedding_algorithm,
            chunking_algorithm=chunking_algorithm,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
            rerank_enabled=rerank_enabled,
            rerank_algorithm=rerank_algorithm,
        )

    def delete_vector_rag_config(self, workspace_id: int, user_id: int) -> bool:
        """
        Delete Vector RAG configuration for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID (for authorization)

        Returns:
            True if deleted, False otherwise
        """
        if not self._validate_workspace_access(workspace_id, user_id):
            return False
        return self.repository.delete_vector_rag_config(workspace_id)

    def _validate_vector_config(
        self,
        embedding_algorithm: str,
        chunking_algorithm: str,
        chunk_size: int,
        chunk_overlap: int,
        top_k: int,
        rerank_algorithm: Optional[str],
    ) -> None:
        """
        Validate Vector RAG configuration data.

        Args:
            embedding_algorithm: The embedding algorithm
            chunking_algorithm: The chunking algorithm
            chunk_size: The chunk size
            chunk_overlap: The chunk overlap
            top_k: The number of top results
            rerank_algorithm: The reranking algorithm

        Raises:
            ValueError: If validation fails
        """
        # Validate embedding algorithm
        valid_embedding_algorithms = ["nomic-embed-text", "all-MiniLM-L6-v2"]
        if embedding_algorithm not in valid_embedding_algorithms:
            raise ValueError(f"embedding_algorithm must be one of: {', '.join(valid_embedding_algorithms)}")

        # Validate chunking algorithm
        valid_chunking_algorithms = ["sentence", "character", "semantic"]
        if chunking_algorithm not in valid_chunking_algorithms:
            raise ValueError(f"chunking_algorithm must be one of: {', '.join(valid_chunking_algorithms)}")

        # Validate chunk_size
        if not (100 <= chunk_size <= 5000):
            raise ValueError("chunk_size must be between 100 and 5000")

        # Validate chunk_overlap
        if not (0 <= chunk_overlap <= 1000):
            raise ValueError("chunk_overlap must be between 0 and 1000")

        # Validate top_k
        if not (1 <= top_k <= 50):
            raise ValueError("top_k must be between 1 and 50")

        # Validate rerank_algorithm if provided
        if rerank_algorithm:
            valid_rerank_algorithms = ["cross-encoder/ms-marco-MiniLM-L-6-v2"]
            if rerank_algorithm not in valid_rerank_algorithms:
                raise ValueError(f"rerank_algorithm must be one of: {', '.join(valid_rerank_algorithms)}")