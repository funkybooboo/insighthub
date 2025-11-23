"""Unit tests for WorkspaceService."""

import pytest
from datetime import datetime
from shared.models.workspace import RagConfig, Workspace
from shared.repositories.workspace import WorkspaceRepository
from shared.types.option import Nothing, Option, Some

from src.domains.workspaces.service import WorkspaceService, WorkspaceStats


class FakeWorkspaceRepository(WorkspaceRepository):
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

    def get_by_id(self, workspace_id: int) -> Option[Workspace]:
        """Get workspace by ID."""
        ws = self.workspaces.get(workspace_id)
        if ws is None:
            return Nothing()
        return Some(ws)

    def get_by_user(self, user_id: int, include_inactive: bool = False) -> list[Workspace]:
        """Get all workspaces for a user."""
        result = []
        for ws in self.workspaces.values():
            if ws.user_id == user_id:
                if include_inactive or ws.is_active:
                    result.append(ws)
        return result

    def update(self, workspace_id: int, **kwargs: str | int | bool | None) -> Option[Workspace]:
        """Update workspace fields."""
        ws = self.workspaces.get(workspace_id)
        if ws is None:
            return Nothing()

        for key, value in kwargs.items():
            if hasattr(ws, key):
                setattr(ws, key, value)
        ws.updated_at = datetime.utcnow()

        return Some(ws)

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

    def get_rag_config(self, workspace_id: int) -> Option[RagConfig]:
        """Get RAG config for workspace."""
        config = self.rag_configs.get(workspace_id)
        if config is None:
            return Nothing()
        return Some(config)

    def update_rag_config(
        self, workspace_id: int, **kwargs: str | int | bool | None
    ) -> Option[RagConfig]:
        """Update RAG config fields."""
        config = self.rag_configs.get(workspace_id)
        if config is None:
            return Nothing()

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.updated_at = datetime.utcnow()

        return Some(config)

    def get_document_count(self, workspace_id: int) -> int:
        """Get document count for workspace."""
        return self.document_counts.get(workspace_id, 0)

    def get_session_count(self, workspace_id: int) -> int:
        """Get session count for workspace."""
        return self.session_counts.get(workspace_id, 0)


@pytest.fixture
def fake_repository() -> FakeWorkspaceRepository:
    """Provide a fake repository."""
    return FakeWorkspaceRepository()


@pytest.fixture
def service(fake_repository: FakeWorkspaceRepository) -> WorkspaceService:
    """Provide a WorkspaceService with fake repository."""
    return WorkspaceService(workspace_repo=fake_repository)


class TestWorkspaceServiceCreate:
    """Tests for workspace creation."""

    def test_create_workspace_returns_workspace(self, service: WorkspaceService) -> None:
        """create_workspace returns a Workspace object."""
        workspace = service.create_workspace(
            name="Test Workspace",
            user_id=1,
            description="Test description",
        )

        assert isinstance(workspace, Workspace)
        assert workspace.id == 1
        assert workspace.name == "Test Workspace"
        assert workspace.user_id == 1
        assert workspace.description == "Test description"

    def test_create_workspace_without_description(self, service: WorkspaceService) -> None:
        """create_workspace works without description."""
        workspace = service.create_workspace(
            name="Minimal Workspace",
            user_id=1,
        )

        assert workspace.name == "Minimal Workspace"
        assert workspace.description is None

    def test_create_workspace_sets_status_to_ready(self, service: WorkspaceService) -> None:
        """create_workspace sets status to ready."""
        workspace = service.create_workspace(
            name="Test",
            user_id=1,
        )

        assert workspace.status == "ready"

    def test_create_workspace_creates_default_rag_config(
        self, service: WorkspaceService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """create_workspace creates default RAG config."""
        workspace = service.create_workspace(
            name="Test",
            user_id=1,
        )

        config = fake_repository.rag_configs.get(workspace.id)
        assert config is not None
        assert config.embedding_model == "nomic-embed-text"
        assert config.retriever_type == "vector"
        assert config.chunk_size == 1000

    def test_create_workspace_with_custom_rag_config(
        self, service: WorkspaceService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """create_workspace creates workspace with custom RAG config."""
        workspace = service.create_workspace(
            name="Custom Config Workspace",
            user_id=1,
            rag_config_data={
                "embedding_model": "text-embedding-3-small",
                "retriever_type": "hybrid",
                "chunk_size": 500,
                "top_k": 10,
            },
        )

        config = fake_repository.rag_configs.get(workspace.id)
        assert config is not None
        assert config.embedding_model == "text-embedding-3-small"
        assert config.retriever_type == "hybrid"
        assert config.chunk_size == 500
        assert config.top_k == 10

    def test_create_workspace_increments_id(self, service: WorkspaceService) -> None:
        """create_workspace assigns incrementing IDs."""
        ws1 = service.create_workspace(name="First", user_id=1)
        ws2 = service.create_workspace(name="Second", user_id=1)
        ws3 = service.create_workspace(name="Third", user_id=1)

        assert ws1.id == 1
        assert ws2.id == 2
        assert ws3.id == 3


class TestWorkspaceServiceList:
    """Tests for listing workspaces."""

    def test_list_workspaces_returns_empty_list(self, service: WorkspaceService) -> None:
        """list_workspaces returns empty list when no workspaces."""
        workspaces = service.list_workspaces(user_id=1)

        assert workspaces == []

    def test_list_workspaces_returns_user_workspaces(self, service: WorkspaceService) -> None:
        """list_workspaces returns workspaces for user."""
        service.create_workspace(name="WS1", user_id=1)
        service.create_workspace(name="WS2", user_id=1)
        service.create_workspace(name="Other User WS", user_id=2)

        workspaces = service.list_workspaces(user_id=1)

        assert len(workspaces) == 2
        assert all(ws.user_id == 1 for ws in workspaces)

    def test_list_workspaces_excludes_inactive_by_default(
        self, service: WorkspaceService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """list_workspaces excludes inactive workspaces by default."""
        ws1 = service.create_workspace(name="Active", user_id=1)
        ws2 = service.create_workspace(name="Inactive", user_id=1)
        fake_repository.update(ws2.id, is_active=False)

        workspaces = service.list_workspaces(user_id=1)

        assert len(workspaces) == 1
        assert workspaces[0].name == "Active"

    def test_list_workspaces_includes_inactive_when_requested(
        self, service: WorkspaceService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """list_workspaces includes inactive when include_inactive=True."""
        ws1 = service.create_workspace(name="Active", user_id=1)
        ws2 = service.create_workspace(name="Inactive", user_id=1)
        fake_repository.update(ws2.id, is_active=False)

        workspaces = service.list_workspaces(user_id=1, include_inactive=True)

        assert len(workspaces) == 2


class TestWorkspaceServiceGet:
    """Tests for getting a workspace."""

    def test_get_workspace_returns_workspace(self, service: WorkspaceService) -> None:
        """get_workspace returns workspace when found."""
        created = service.create_workspace(name="Test", user_id=1)

        workspace = service.get_workspace(workspace_id=created.id, user_id=1)

        assert workspace is not None
        assert workspace.id == created.id
        assert workspace.name == "Test"

    def test_get_workspace_returns_none_for_nonexistent(self, service: WorkspaceService) -> None:
        """get_workspace returns None when workspace doesn't exist."""
        workspace = service.get_workspace(workspace_id=999, user_id=1)

        assert workspace is None

    def test_get_workspace_returns_none_for_wrong_user(self, service: WorkspaceService) -> None:
        """get_workspace returns None when user doesn't own workspace."""
        created = service.create_workspace(name="Test", user_id=1)

        workspace = service.get_workspace(workspace_id=created.id, user_id=2)

        assert workspace is None

    def test_get_workspace_accepts_string_id(self, service: WorkspaceService) -> None:
        """get_workspace accepts string workspace_id."""
        created = service.create_workspace(name="Test", user_id=1)

        workspace = service.get_workspace(workspace_id="1", user_id=1)

        assert workspace is not None
        assert workspace.id == 1


class TestWorkspaceServiceUpdate:
    """Tests for updating a workspace."""

    def test_update_workspace_returns_updated_workspace(self, service: WorkspaceService) -> None:
        """update_workspace returns updated workspace."""
        created = service.create_workspace(name="Original", user_id=1)

        updated = service.update_workspace(
            workspace_id=created.id,
            user_id=1,
            name="Updated Name",
            description="New description",
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "New description"

    def test_update_workspace_returns_none_for_nonexistent(
        self, service: WorkspaceService
    ) -> None:
        """update_workspace returns None for nonexistent workspace."""
        result = service.update_workspace(
            workspace_id=999,
            user_id=1,
            name="Updated",
        )

        assert result is None

    def test_update_workspace_returns_none_for_wrong_user(self, service: WorkspaceService) -> None:
        """update_workspace returns None when user doesn't own workspace."""
        created = service.create_workspace(name="Test", user_id=1)

        result = service.update_workspace(
            workspace_id=created.id,
            user_id=2,
            name="Hacked",
        )

        assert result is None


class TestWorkspaceServiceDelete:
    """Tests for deleting a workspace."""

    def test_delete_workspace_returns_true(self, service: WorkspaceService) -> None:
        """delete_workspace returns True when deleted."""
        created = service.create_workspace(name="To Delete", user_id=1)

        result = service.delete_workspace(workspace_id=created.id, user_id=1)

        assert result is True

    def test_delete_workspace_removes_workspace(self, service: WorkspaceService) -> None:
        """delete_workspace removes the workspace."""
        created = service.create_workspace(name="To Delete", user_id=1)
        service.delete_workspace(workspace_id=created.id, user_id=1)

        workspace = service.get_workspace(workspace_id=created.id, user_id=1)
        assert workspace is None

    def test_delete_workspace_returns_false_for_nonexistent(
        self, service: WorkspaceService
    ) -> None:
        """delete_workspace returns False for nonexistent workspace."""
        result = service.delete_workspace(workspace_id=999, user_id=1)

        assert result is False

    def test_delete_workspace_returns_false_for_wrong_user(
        self, service: WorkspaceService
    ) -> None:
        """delete_workspace returns False when user doesn't own workspace."""
        created = service.create_workspace(name="Test", user_id=1)

        result = service.delete_workspace(workspace_id=created.id, user_id=2)

        assert result is False


class TestWorkspaceServiceStats:
    """Tests for workspace statistics."""

    def test_get_workspace_stats_returns_stats(
        self, service: WorkspaceService, fake_repository: FakeWorkspaceRepository
    ) -> None:
        """get_workspace_stats returns WorkspaceStats."""
        created = service.create_workspace(name="Test", user_id=1)
        fake_repository.document_counts[created.id] = 5
        fake_repository.session_counts[created.id] = 3

        stats = service.get_workspace_stats(workspace_id=created.id, user_id=1)

        assert stats is not None
        assert isinstance(stats, WorkspaceStats)
        assert stats.workspace_id == created.id
        assert stats.document_count == 5
        assert stats.chat_session_count == 3

    def test_get_workspace_stats_returns_none_for_nonexistent(
        self, service: WorkspaceService
    ) -> None:
        """get_workspace_stats returns None for nonexistent workspace."""
        stats = service.get_workspace_stats(workspace_id=999, user_id=1)

        assert stats is None

    def test_get_workspace_stats_returns_none_for_wrong_user(
        self, service: WorkspaceService
    ) -> None:
        """get_workspace_stats returns None when user doesn't own workspace."""
        created = service.create_workspace(name="Test", user_id=1)

        stats = service.get_workspace_stats(workspace_id=created.id, user_id=2)

        assert stats is None


class TestWorkspaceServiceRagConfig:
    """Tests for RAG configuration operations."""

    def test_get_rag_config_returns_config(self, service: WorkspaceService) -> None:
        """get_rag_config returns RagConfig."""
        created = service.create_workspace(name="Test", user_id=1)

        config = service.get_rag_config(workspace_id=created.id, user_id=1)

        assert config is not None
        assert isinstance(config, RagConfig)
        assert config.workspace_id == created.id

    def test_get_rag_config_returns_none_for_nonexistent(self, service: WorkspaceService) -> None:
        """get_rag_config returns None for nonexistent workspace."""
        config = service.get_rag_config(workspace_id=999, user_id=1)

        assert config is None

    def test_get_rag_config_returns_none_for_wrong_user(self, service: WorkspaceService) -> None:
        """get_rag_config returns None when user doesn't own workspace."""
        created = service.create_workspace(name="Test", user_id=1)

        config = service.get_rag_config(workspace_id=created.id, user_id=2)

        assert config is None

    def test_update_rag_config_returns_updated_config(self, service: WorkspaceService) -> None:
        """update_rag_config returns updated RagConfig."""
        created = service.create_workspace(name="Test", user_id=1)

        updated = service.update_rag_config(
            workspace_id=created.id,
            user_id=1,
            retriever_type="graph",
            chunk_size=500,
            top_k=15,
        )

        assert updated is not None
        assert updated.retriever_type == "graph"
        assert updated.chunk_size == 500
        assert updated.top_k == 15

    def test_update_rag_config_returns_none_for_nonexistent(
        self, service: WorkspaceService
    ) -> None:
        """update_rag_config returns None for nonexistent workspace."""
        result = service.update_rag_config(
            workspace_id=999,
            user_id=1,
            chunk_size=500,
        )

        assert result is None


class TestWorkspaceServiceValidateAccess:
    """Tests for workspace access validation."""

    def test_validate_workspace_access_returns_true(self, service: WorkspaceService) -> None:
        """validate_workspace_access returns True for owner."""
        created = service.create_workspace(name="Test", user_id=1)

        result = service.validate_workspace_access(workspace_id=created.id, user_id=1)

        assert result is True

    def test_validate_workspace_access_returns_false_for_nonexistent(
        self, service: WorkspaceService
    ) -> None:
        """validate_workspace_access returns False for nonexistent workspace."""
        result = service.validate_workspace_access(workspace_id=999, user_id=1)

        assert result is False

    def test_validate_workspace_access_returns_false_for_wrong_user(
        self, service: WorkspaceService
    ) -> None:
        """validate_workspace_access returns False when user doesn't own workspace."""
        created = service.create_workspace(name="Test", user_id=1)

        result = service.validate_workspace_access(workspace_id=created.id, user_id=2)

        assert result is False
