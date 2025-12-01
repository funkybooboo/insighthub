"""Unit tests for workspace domain."""

import pytest

from src.domains.workspaces.service import WorkspaceService
from src.infrastructure.repositories.workspaces.in_memory_workspace_repository import (
    InMemoryWorkspaceRepository,
)


@pytest.mark.unit
class TestWorkspaceService:
    """Test cases for WorkspaceService."""

    @pytest.fixture
    def workspace_repository(self):
        """Create a fresh in-memory workspace repository for each test."""
        return InMemoryWorkspaceRepository()

    @pytest.fixture
    def workspace_service(self, workspace_repository):
        """Create a WorkspaceService with in-memory repository."""
        return WorkspaceService(workspace_repository)

    def test_create_workspace_success_vector(self, workspace_service):
        """Test successful workspace creation with vector RAG."""
        workspace = workspace_service.create_workspace(
            user_id=1, name="Test Workspace", description="A test workspace", rag_type="vector"
        )

        assert workspace.id is not None
        assert workspace.user_id == 1
        assert workspace.name == "Test Workspace"
        assert workspace.description == "A test workspace"
        assert workspace.rag_type == "vector"
        assert workspace.status == "provisioning"

    def test_create_workspace_success_graph(self, workspace_service):
        """Test successful workspace creation with graph RAG."""
        workspace = workspace_service.create_workspace(
            user_id=1, name="Graph Workspace", rag_type="graph"
        )

        assert workspace.rag_type == "graph"
        assert workspace.status == "provisioning"

    def test_create_workspace_empty_name(self, workspace_service):
        """Test workspace creation with empty name raises error."""
        with pytest.raises(ValueError, match="Workspace name cannot be empty"):
            workspace_service.create_workspace(user_id=1, name="")

    def test_create_workspace_name_too_long(self, workspace_service):
        """Test workspace creation with name too long raises error."""
        long_name = "a" * 256
        with pytest.raises(ValueError, match="Workspace name too long"):
            workspace_service.create_workspace(user_id=1, name=long_name)

    def test_create_workspace_description_too_long(self, workspace_service):
        """Test workspace creation with description too long raises error."""
        long_description = "a" * 1001
        with pytest.raises(ValueError, match="Workspace description too long"):
            workspace_service.create_workspace(user_id=1, name="Test", description=long_description)

    def test_create_workspace_invalid_rag_type(self, workspace_service):
        """Test workspace creation with invalid RAG type raises error."""
        with pytest.raises(ValueError, match="Invalid rag_type"):
            workspace_service.create_workspace(user_id=1, name="Test", rag_type="invalid")

    def test_create_workspace_with_vector_rag_config(self, workspace_service):
        """Test workspace creation with vector RAG config."""
        rag_config = {
            "embedding_algorithm": "ollama",
            "chunking_algorithm": "sentence",
            "rerank_algorithm": "none",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 5,
        }

        workspace = workspace_service.create_workspace(
            user_id=1, name="Test Workspace", rag_type="vector", rag_config=rag_config
        )

        assert workspace.rag_type == "vector"

        # Check that RAG config was stored
        config = workspace_service.get_vector_rag_config(workspace.id)
        assert config is not None
        assert config.embedding_algorithm == "ollama"
        assert config.chunk_size == 1000

    def test_create_workspace_with_invalid_vector_config(self, workspace_service):
        """Test workspace creation with invalid vector RAG config raises error."""
        rag_config = {
            "embedding_algorithm": "ollama",
            # Missing required fields
        }

        with pytest.raises(ValueError, match="Missing required field"):
            workspace_service.create_workspace(
                user_id=1, name="Test", rag_type="vector", rag_config=rag_config
            )

    def test_get_workspace_existing(self, workspace_service):
        """Test getting existing workspace."""
        created = workspace_service.create_workspace(user_id=1, name="Test")

        retrieved = workspace_service.get_workspace(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test"

    def test_get_workspace_nonexistent(self, workspace_service):
        """Test getting nonexistent workspace returns None."""
        workspace = workspace_service.get_workspace(999)
        assert workspace is None

    def test_list_user_workspaces(self, workspace_service):
        """Test listing workspaces for a user."""
        # Create workspaces for different users
        workspace_service.create_workspace(user_id=1, name="User1 WS1")
        workspace_service.create_workspace(user_id=1, name="User1 WS2")
        workspace_service.create_workspace(user_id=2, name="User2 WS1")

        user1_workspaces = workspace_service.list_user_workspaces(1)
        user2_workspaces = workspace_service.list_user_workspaces(2)

        assert len(user1_workspaces) == 2
        assert len(user2_workspaces) == 1
        assert user1_workspaces[0].name == "User1 WS1"
        assert user1_workspaces[1].name == "User1 WS2"
        assert user2_workspaces[0].name == "User2 WS1"

    def test_update_workspace_success(self, workspace_service):
        """Test successful workspace update."""
        workspace = workspace_service.create_workspace(user_id=1, name="Original Name")

        updated = workspace_service.update_workspace(
            workspace.id, name="Updated Name", description="Updated Description"
        )

        assert updated is not None
        assert updated.id == workspace.id
        assert updated.name == "Updated Name"
        assert updated.description == "Updated Description"

    def test_update_workspace_empty_name(self, workspace_service):
        """Test workspace update with empty name raises error."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test")

        with pytest.raises(ValueError, match="Workspace name cannot be empty"):
            workspace_service.update_workspace(workspace.id, name="")

    def test_update_workspace_nonexistent(self, workspace_service):
        """Test updating nonexistent workspace returns None."""
        result = workspace_service.update_workspace(999, name="New Name")
        assert result is None

    def test_delete_workspace_success(self, workspace_service):
        """Test successful workspace deletion initiation."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test")

        result = workspace_service.delete_workspace(workspace.id, user_id=1)
        assert result is True

        # Verify workspace status is updated to 'deleting'
        retrieved = workspace_service.get_workspace(workspace.id)
        assert retrieved is not None
        assert retrieved.status == "deleting"

    def test_delete_workspace_nonexistent(self, workspace_service):
        """Test deleting nonexistent workspace returns False."""
        result = workspace_service.delete_workspace(999, user_id=1)
        assert result is False

    def test_get_rag_config_vector_default(self, workspace_service):
        """Test getting default vector RAG config."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="vector")

        config = workspace_service.get_rag_config(workspace.id)
        assert config is not None
        assert config.rag_type == "vector"
        assert config.config["embedding_algorithm"] == "ollama"
        assert config.config["chunk_size"] == 1000

    def test_get_rag_config_graph_default(self, workspace_service):
        """Test getting default graph RAG config."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="graph")

        config = workspace_service.get_rag_config(workspace.id)
        assert config is not None
        assert config.rag_type == "graph"
        assert config.config["entity_extraction_algorithm"] == "spacy"

    def test_get_rag_config_nonexistent_workspace(self, workspace_service):
        """Test getting RAG config for nonexistent workspace returns None."""
        config = workspace_service.get_rag_config(999)
        assert config is None

    def test_get_vector_rag_config_existing(self, workspace_service):
        """Test getting existing vector RAG config."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="vector")

        # Create a config
        workspace_service.create_vector_rag_config(
            workspace_id=workspace.id, embedding_algorithm="openai", chunk_size=500
        )

        retrieved = workspace_service.get_vector_rag_config(workspace.id)
        assert retrieved is not None
        assert retrieved.embedding_algorithm == "openai"
        assert retrieved.chunk_size == 500

    def test_get_vector_rag_config_wrong_type(self, workspace_service):
        """Test getting vector RAG config for graph workspace returns None."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="graph")

        config = workspace_service.get_vector_rag_config(workspace.id)
        assert config is None

    def test_validate_workspace_access_success(self, workspace_service):
        """Test successful workspace access validation."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test")

        result = workspace_service.validate_workspace_access(workspace.id, user_id=1)
        assert result is True

    def test_validate_workspace_access_wrong_user(self, workspace_service):
        """Test workspace access validation with wrong user returns False."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test")

        result = workspace_service.validate_workspace_access(workspace.id, user_id=2)
        assert result is False

    def test_validate_workspace_access_nonexistent(self, workspace_service):
        """Test workspace access validation for nonexistent workspace returns False."""
        result = workspace_service.validate_workspace_access(999, user_id=1)
        assert result is False

    def test_get_user_workspace_success(self, workspace_service):
        """Test getting workspace for correct user."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test")

        result = workspace_service.get_user_workspace(workspace.id, user_id=1)
        assert result is not None
        assert result.id == workspace.id

    def test_get_user_workspace_wrong_user(self, workspace_service):
        """Test getting workspace for wrong user returns None."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test")

        result = workspace_service.get_user_workspace(workspace.id, user_id=2)
        assert result is None

    def test_create_vector_rag_config_success(self, workspace_service):
        """Test successful vector RAG config creation."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="vector")

        config = workspace_service.create_vector_rag_config(
            workspace_id=workspace.id, embedding_algorithm="openai", chunk_size=500, top_k=10
        )

        assert config.workspace_id == workspace.id
        assert config.embedding_algorithm == "openai"
        assert config.chunk_size == 500
        assert config.top_k == 10

    def test_create_vector_rag_config_wrong_workspace_type(self, workspace_service):
        """Test vector RAG config creation for graph workspace raises error."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="graph")

        with pytest.raises(ValueError, match="not a vector RAG workspace"):
            workspace_service.create_vector_rag_config(workspace_id=workspace.id)

    def test_create_vector_rag_config_nonexistent_workspace(self, workspace_service):
        """Test vector RAG config creation for nonexistent workspace raises error."""
        with pytest.raises(ValueError, match="not found"):
            workspace_service.create_vector_rag_config(workspace_id=999)

    def test_update_vector_rag_config_success(self, workspace_service):
        """Test successful vector RAG config update."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="vector")
        workspace_service.create_vector_rag_config(workspace_id=workspace.id, chunk_size=1000)

        updated = workspace_service.update_vector_rag_config(
            workspace_id=workspace.id, chunk_size=1500, top_k=20
        )

        assert updated is not None
        assert updated.chunk_size == 1500
        assert updated.top_k == 20

    def test_update_vector_rag_config_nonexistent_workspace(self, workspace_service):
        """Test vector RAG config update for nonexistent workspace returns None."""
        result = workspace_service.update_vector_rag_config(workspace_id=999, chunk_size=500)
        assert result is None

    def test_create_graph_rag_config_success(self, workspace_service):
        """Test successful graph RAG config creation."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="graph")

        config = workspace_service.create_graph_rag_config(
            workspace_id=workspace.id,
            entity_extraction_algorithm="nltk",
            clustering_algorithm="louvain",
        )

        assert config.workspace_id == workspace.id
        assert config.entity_extraction_algorithm == "nltk"
        assert config.clustering_algorithm == "louvain"

    def test_create_graph_rag_config_wrong_workspace_type(self, workspace_service):
        """Test graph RAG config creation for vector workspace raises error."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="vector")

        with pytest.raises(ValueError, match="not a graph RAG workspace"):
            workspace_service.create_graph_rag_config(workspace_id=workspace.id)

    def test_update_graph_rag_config_success(self, workspace_service):
        """Test successful graph RAG config update."""
        workspace = workspace_service.create_workspace(user_id=1, name="Test", rag_type="graph")
        workspace_service.create_graph_rag_config(workspace_id=workspace.id)

        updated = workspace_service.update_graph_rag_config(
            workspace_id=workspace.id,
            entity_extraction_algorithm="spacy",
            clustering_algorithm="leiden",
        )

        assert updated is not None
        assert updated.entity_extraction_algorithm == "spacy"
        assert updated.clustering_algorithm == "leiden"
