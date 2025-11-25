"""Unit tests for RagConfigService using dummy implementations."""

from datetime import datetime
from typing import Any

import pytest
from shared.models.workspace import RagConfig, Workspace

from src.domains.workspaces.rag_config.service import RagConfigService


class FakeWorkspaceRepository:
    """Fake workspace repository for testing."""

    def __init__(self) -> None:
        """Initialize with in-memory storage."""
        self.workspaces: dict[int, Workspace] = {}
        self.rag_configs: dict[int, RagConfig] = {}
        self.next_ws_id = 1
        self.next_config_id = 1
        self.document_counts: dict[int, int] = {}
        self.session_counts: dict[int, int] = {}

    def create(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
    ) -> Workspace:
        """Create a new workspace."""
        workspace = Workspace(
            id=self.next_ws_id,
            user_id=user_id,
            name=name,
            description=description,
            is_active=True,
            status="provisioning",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.workspaces[workspace.id] = workspace
        self.next_ws_id += 1
        return workspace

    def get_by_id(self, workspace_id: int) -> Workspace | None:
        """Get workspace by ID."""
        return self.workspaces.get(workspace_id)

    def get_by_user(self, user_id: int, include_inactive: bool = False) -> list[Workspace]:
        """Get all workspaces for a user."""
        result = []
        for ws in self.workspaces.values():
            if ws.user_id == user_id and (include_inactive or ws.is_active):
                result.append(ws)
        return result

    def update(self, workspace_id: int, **kwargs: Any) -> Workspace | None:
        """Update workspace fields."""
        ws = self.workspaces.get(workspace_id)
        if ws is None:
            return None

        for key, value in kwargs.items():
            if hasattr(ws, key):
                setattr(ws, key, value)
        ws.updated_at = datetime.utcnow()

        return ws

    def delete(self, workspace_id: int) -> bool:
        """Delete workspace by ID."""
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
            if workspace_id in self.rag_configs:
                del self.rag_configs[workspace_id]
            return True
        return False

    def create_rag_config(
        self,
        workspace_id: int,
        embedding_model: str = "nomic-embed-text",
        embedding_dim: int | None = None,
        retriever_type: str = "vector",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 8,
        rerank_enabled: bool = False,
        rerank_model: str | None = None,
    ) -> RagConfig:
        """Create RAG config for workspace."""
        config = RagConfig(
            id=self.next_config_id,
            workspace_id=workspace_id,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
            retriever_type=retriever_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
            rerank_enabled=rerank_enabled,
            rerank_model=rerank_model,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.rag_configs[workspace_id] = config
        self.next_config_id += 1
        return config

    def get_rag_config(self, workspace_id: int) -> RagConfig | None:
        """Get RAG config for workspace."""
        return self.rag_configs.get(workspace_id)

    def update_rag_config(self, workspace_id: int, **kwargs: Any) -> RagConfig | None:
        """Update RAG config fields."""
        config = self.rag_configs.get(workspace_id)
        if config is None:
            return None

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.updated_at = datetime.utcnow()

        return config

    def get_document_count(self, workspace_id: int) -> int:
        """Get document count for workspace."""
        return self.document_counts.get(workspace_id, 0)

    def get_session_count(self, workspace_id: int) -> int:
        """Get session count for workspace."""
        return self.session_counts.get(workspace_id, 0)


class FakeWorkspaceService:
    """Fake workspace service for testing."""

    def __init__(self, repository: FakeWorkspaceRepository):
        """Initialize with repository."""
        self.repository = repository

    def validate_workspace_access(self, workspace_id: int, user_id: int) -> bool:
        """Validate workspace access."""
        workspace = self.repository.get_by_id(workspace_id)
        return workspace is not None and workspace.user_id == user_id


@pytest.fixture
def fake_repository() -> FakeWorkspaceRepository:
    """Provide a fake repository."""
    return FakeWorkspaceRepository()


@pytest.fixture
def fake_workspace_service(fake_repository: FakeWorkspaceRepository) -> FakeWorkspaceService:
    """Provide a fake workspace service."""
    return FakeWorkspaceService(fake_repository)


@pytest.fixture
def service(
    fake_repository: FakeWorkspaceRepository, fake_workspace_service: FakeWorkspaceService
) -> RagConfigService:
    """Provide a RagConfigService with fake dependencies."""
    return RagConfigService(fake_repository, fake_workspace_service)  # type: ignore


class TestRagConfigServiceGet:
    """Tests for getting RAG configurations."""

    def test_get_rag_config_returns_config_when_exists(
        self,
        service: RagConfigService,
        fake_repository: FakeWorkspaceRepository,
        fake_workspace_service: FakeWorkspaceService,
    ) -> None:
        """Test getting RAG config when it exists."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        config = fake_repository.create_rag_config(
            workspace_id=workspace.id, embedding_model="custom-model", chunk_size=1500
        )

        # Execute
        result = service.get_rag_config(workspace.id, workspace.user_id)

        # Assert
        assert result is not None
        assert result.id == config.id
        assert result.workspace_id == workspace.id
        assert result.embedding_model == "custom-model"
        assert result.chunk_size == 1500

    def test_get_rag_config_returns_none_when_not_exists(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test getting RAG config when it doesn't exist."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")

        # Execute
        result = service.get_rag_config(workspace.id, workspace.user_id)

        # Assert
        assert result is None

    def test_get_rag_config_returns_none_when_no_access(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test getting RAG config when user has no access."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.get_rag_config(workspace.id, user_id=999)  # Different user

        # Assert
        assert result is None


class TestRagConfigServiceCreate:
    """Tests for creating RAG configurations."""

    def test_create_rag_config_success(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test creating RAG config successfully."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")

        # Execute
        result = service.create_rag_config(
            workspace.id,
            workspace.user_id,
            embedding_model="custom-model",
            chunk_size=1500,
            top_k=10,
        )

        # Assert
        assert result is not None
        assert result.workspace_id == workspace.id
        assert result.embedding_model == "custom-model"
        assert result.chunk_size == 1500
        assert result.top_k == 10
        assert result.retriever_type == "vector"  # default

    def test_create_rag_config_raises_error_when_already_exists(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test creating RAG config when it already exists."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="already exists"):
            service.create_rag_config(workspace.id, workspace.user_id)

    def test_create_rag_config_raises_error_when_no_access(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test creating RAG config when user has no access."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")

        # Execute & Assert
        with pytest.raises(ValueError, match="No access to workspace"):
            service.create_rag_config(workspace.id, user_id=999)


class TestRagConfigServiceUpdate:
    """Tests for updating RAG configurations."""

    def test_update_rag_config_success(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test updating RAG config successfully."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id, chunk_size=1000)

        # Execute
        result = service.update_rag_config(
            workspace.id, workspace.user_id, chunk_size=2000, top_k=15
        )

        # Assert
        assert result is not None
        assert result.chunk_size == 2000
        assert result.top_k == 15

    def test_update_rag_config_returns_none_when_no_access(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test updating RAG config when user has no access."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, user_id=999, chunk_size=2000)

        # Assert
        assert result is None

    def test_update_rag_config_returns_none_when_config_not_exists(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test updating RAG config when it doesn't exist."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_size=2000)

        # Assert
        assert result is None


class TestRagConfigServiceDelete:
    """Tests for deleting RAG configurations."""

    def test_delete_rag_config_success(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test deleting RAG config successfully."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.delete_rag_config(workspace.id, workspace.user_id)

        # Assert
        assert result is True
        assert fake_repository.get_rag_config(workspace.id) is None

    def test_delete_rag_config_returns_false_when_no_access(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test deleting RAG config when user has no access."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.delete_rag_config(workspace.id, user_id=999)

        # Assert
        assert result is False
        assert fake_repository.get_rag_config(workspace.id) is not None


class TestRagConfigServiceValidation:
    """Tests for RAG configuration validation."""

    def test_update_validates_retriever_type_vector(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts valid retriever_type 'vector'."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, retriever_type="vector")

        # Assert
        assert result is not None
        assert result.retriever_type == "vector"

    def test_update_validates_retriever_type_graph(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts valid retriever_type 'graph'."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, retriever_type="graph")

        # Assert
        assert result is not None
        assert result.retriever_type == "graph"

    def test_update_validates_retriever_type_hybrid(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts valid retriever_type 'hybrid'."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, retriever_type="hybrid")

        # Assert
        assert result is not None
        assert result.retriever_type == "hybrid"

    def test_update_rejects_invalid_retriever_type(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects invalid retriever_type."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="retriever_type must be one of"):
            service.update_rag_config(workspace.id, workspace.user_id, retriever_type="invalid")

    def test_update_validates_chunk_size_minimum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts minimum chunk_size."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_size=100)

        # Assert
        assert result is not None
        assert result.chunk_size == 100

    def test_update_validates_chunk_size_maximum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts maximum chunk_size."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_size=5000)

        # Assert
        assert result is not None
        assert result.chunk_size == 5000

    def test_update_rejects_chunk_size_too_small(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects chunk_size below minimum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_size must be between 100 and 5000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_size=99)

    def test_update_rejects_chunk_size_too_large(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects chunk_size above maximum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_size must be between 100 and 5000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_size=5001)

    def test_update_validates_chunk_overlap_minimum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts minimum chunk_overlap."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=0)

        # Assert
        assert result is not None
        assert result.chunk_overlap == 0

    def test_update_validates_chunk_overlap_maximum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts maximum chunk_overlap."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=1000)

        # Assert
        assert result is not None
        assert result.chunk_overlap == 1000

    def test_update_rejects_negative_chunk_overlap(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects negative chunk_overlap."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_overlap must be between 0 and 1000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=-1)

    def test_update_rejects_chunk_overlap_too_large(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects chunk_overlap above maximum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_overlap must be between 0 and 1000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=1001)

    def test_update_validates_top_k_minimum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts minimum top_k."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, top_k=1)

        # Assert
        assert result is not None
        assert result.top_k == 1

    def test_update_validates_top_k_maximum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts maximum top_k."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, top_k=50)

        # Assert
        assert result is not None
        assert result.top_k == 50

    def test_update_rejects_top_k_too_small(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects top_k below minimum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
            service.update_rag_config(workspace.id, workspace.user_id, top_k=0)

    def test_update_rejects_top_k_too_large(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects top_k above maximum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
            service.update_rag_config(workspace.id, workspace.user_id, top_k=51)

    def test_update_validates_embedding_model_not_empty(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts non-empty embedding_model."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(
            workspace.id, workspace.user_id, embedding_model="valid-model"
        )

        # Assert
        assert result is not None
        assert result.embedding_model == "valid-model"

    def test_update_rejects_empty_embedding_model(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects empty embedding_model."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="embedding_model cannot be empty"):
            service.update_rag_config(workspace.id, workspace.user_id, embedding_model="")

    def test_update_rejects_whitespace_only_embedding_model(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects whitespace-only embedding_model."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="embedding_model cannot be empty"):
            service.update_rag_config(workspace.id, workspace.user_id, embedding_model="   ")

    def test_update_validates_chunk_size_at_minimum_boundary(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts chunk_size exactly at minimum boundary."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_size=100)

        # Assert
        assert result is not None
        assert result.chunk_size == 100

    def test_update_validates_chunk_size_at_maximum_boundary(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts chunk_size exactly at maximum boundary."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_size=5000)

        # Assert
        assert result is not None
        assert result.chunk_size == 5000

    def test_update_validates_chunk_overlap_at_minimum_boundary(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts chunk_overlap exactly at minimum boundary."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=0)

        # Assert
        assert result is not None
        assert result.chunk_overlap == 0

    def test_update_validates_chunk_overlap_at_maximum_boundary(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts chunk_overlap exactly at maximum boundary."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=1000)

        # Assert
        assert result is not None
        assert result.chunk_overlap == 1000

    def test_update_validates_top_k_at_minimum_boundary(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts top_k exactly at minimum boundary."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, top_k=1)

        # Assert
        assert result is not None
        assert result.top_k == 1

    def test_update_validates_top_k_at_maximum_boundary(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts top_k exactly at maximum boundary."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, top_k=50)

        # Assert
        assert result is not None
        assert result.top_k == 50

    def test_update_rejects_chunk_size_one_below_minimum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects chunk_size one below minimum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_size must be between 100 and 5000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_size=99)

    def test_update_rejects_chunk_size_one_above_maximum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects chunk_size one above maximum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_size must be between 100 and 5000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_size=5001)

    def test_update_rejects_chunk_overlap_one_below_minimum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects chunk_overlap one below minimum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_overlap must be between 0 and 1000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=-1)

    def test_update_rejects_chunk_overlap_one_above_maximum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects chunk_overlap one above maximum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_overlap must be between 0 and 1000"):
            service.update_rag_config(workspace.id, workspace.user_id, chunk_overlap=1001)

    def test_update_rejects_top_k_one_below_minimum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects top_k one below minimum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
            service.update_rag_config(workspace.id, workspace.user_id, top_k=0)

    def test_update_rejects_top_k_one_above_maximum(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects top_k one above maximum."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
            service.update_rag_config(workspace.id, workspace.user_id, top_k=51)

    def test_update_accepts_valid_embedding_model_with_special_characters(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts embedding model names with special characters."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(
            workspace.id, workspace.user_id, embedding_model="model-v2.1_final"
        )

        # Assert
        assert result is not None
        assert result.embedding_model == "model-v2.1_final"

    def test_update_accepts_valid_embedding_model_with_numbers(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation accepts embedding model names with numbers."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(
            workspace.id, workspace.user_id, embedding_model="embedding-model-3"
        )

        # Assert
        assert result is not None
        assert result.embedding_model == "embedding-model-3"

    def test_update_rejects_embedding_model_with_only_numbers(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation rejects embedding model names that are only numbers."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="embedding_model cannot be empty"):
            service.update_rag_config(workspace.id, workspace.user_id, embedding_model="123")

    def test_update_accepts_multiple_validation_fields_at_once(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation when multiple fields are updated simultaneously."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute
        result = service.update_rag_config(
            workspace.id,
            workspace.user_id,
            retriever_type="graph",
            chunk_size=2000,
            chunk_overlap=300,
            top_k=25,
            embedding_model="custom-model",
        )

        # Assert
        assert result is not None
        assert result.retriever_type == "graph"
        assert result.chunk_size == 2000
        assert result.chunk_overlap == 300
        assert result.top_k == 25
        assert result.embedding_model == "custom-model"

    def test_update_fails_when_one_field_invalid_among_valid_ones(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test validation fails when one field is invalid even if others are valid."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        fake_repository.create_rag_config(workspace_id=workspace.id)

        # Execute & Assert
        with pytest.raises(ValueError, match="retriever_type must be one of"):
            service.update_rag_config(
                workspace.id,
                workspace.user_id,
                retriever_type="invalid",  # Invalid
                chunk_size=2000,  # Valid
                embedding_model="model",  # Valid
            )

    def test_update_accepts_empty_update_data_dict(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test update accepts empty dictionary (no changes)."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")
        original_config = fake_repository.create_rag_config(
            workspace_id=workspace.id, chunk_size=1000
        )

        # Execute
        result = service.update_rag_config(workspace.id, workspace.user_id, **{})

        # Assert - should return the original config unchanged
        assert result is not None
        assert result.chunk_size == original_config.chunk_size

    def test_create_accepts_all_valid_parameters_at_once(
        self, service: RagConfigService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """Test create accepts all valid parameters simultaneously."""
        # Setup
        workspace = fake_repository.create(user_id=1, name="test workspace")

        # Execute
        result = service.create_rag_config(
            workspace.id,
            workspace.user_id,
            embedding_model="test-model",
            embedding_dim=512,
            retriever_type="hybrid",
            chunk_size=1500,
            chunk_overlap=250,
            top_k=20,
            rerank_enabled=True,
            rerank_model="rerank-model",
        )

        # Assert
        assert result is not None
        assert result.embedding_model == "test-model"
        assert result.embedding_dim == 512
        assert result.retriever_type == "hybrid"
        assert result.chunk_size == 1500
        assert result.chunk_overlap == 250
        assert result.top_k == 20
        assert result.rerank_enabled is True
        assert result.rerank_model == "rerank-model"
