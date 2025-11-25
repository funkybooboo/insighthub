"""Integration tests for RAG config functionality."""

from typing import Any


class TestRagConfigIntegration:
    """Integration tests for RAG config CRUD operations."""

    def test_full_rag_config_lifecycle(
        self, client: Any, auth_token: str, test_workspace: dict
    ) -> None:
        """Test complete RAG config lifecycle: create, read, update, delete."""
        workspace_id = test_workspace["id"]

        # 1. Initially no RAG config exists
        response = client.get(
            f"/api/workspaces/{workspace_id}/rag-config",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404

        # 2. Create RAG config
        create_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
            "rerank_enabled": False,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201
        created_data = response.get_json()
        assert created_data["workspace_id"] == workspace_id
        assert created_data["embedding_model"] == "nomic-embed-text"
        assert created_data["chunk_size"] == 1000
        config_id = created_data["id"]

        # 3. Read RAG config
        response = client.get(
            f"/api/workspaces/{workspace_id}/rag-config",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        read_data = response.get_json()
        assert read_data["id"] == config_id
        assert read_data["workspace_id"] == workspace_id
        assert read_data["embedding_model"] == "nomic-embed-text"

        # 4. Update RAG config
        update_data = {
            "chunk_size": 1200,
            "top_k": 10,
            "rerank_enabled": True,
            "rerank_model": "rerank-model-v1",
        }
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        updated_data = response.get_json()
        assert updated_data["chunk_size"] == 1200
        assert updated_data["top_k"] == 10
        assert updated_data["rerank_enabled"] is True
        assert updated_data["rerank_model"] == "rerank-model-v1"

        # 5. Verify update persisted
        response = client.get(
            f"/api/workspaces/{workspace_id}/rag-config",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        verify_data = response.get_json()
        assert verify_data["chunk_size"] == 1200
        assert verify_data["top_k"] == 10

    def test_create_duplicate_rag_config(
        self, client: Any, auth_token: str, test_workspace: dict
    ) -> None:
        """Test creating duplicate RAG config fails."""
        workspace_id = test_workspace["id"]

        # Create initial RAG config
        create_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Try to create another RAG config - should fail
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 409

    def test_rag_config_validation(
        self, client: Any, auth_token: str, test_workspace: dict
    ) -> None:
        """Test RAG config validation."""
        workspace_id = test_workspace["id"]

        # Test invalid embedding model
        invalid_data = {
            "embedding_model": "invalid-model",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test invalid retriever type
        invalid_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "invalid-type",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

    def test_rag_config_access_control(
        self, client: Any, auth_token: str, test_workspace: dict
    ) -> None:
        """Test RAG config access control."""
        workspace_id = test_workspace["id"]

        # Create RAG config
        create_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Try to access from different workspace - should fail
        # This test assumes we have another workspace, but for now we'll skip this
        # TODO: Add multi-workspace access control test

    def test_rag_config_update_validation(
        self, client: Any, auth_token: str, test_workspace: dict
    ) -> None:
        """Test RAG config update validation."""
        workspace_id = test_workspace["id"]

        # Create initial RAG config
        create_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Test invalid chunk size (too small)
        update_data = {"chunk_size": 50}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test invalid chunk size (too large)
        update_data = {"chunk_size": 10000}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test invalid chunk overlap (negative)
        update_data = {"chunk_overlap": -1}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test invalid top_k (too small)
        update_data = {"top_k": 0}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test invalid top_k (too large)
        update_data = {"top_k": 100}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

    def test_rag_config_partial_updates(
        self, client: Any, auth_token: str, test_workspace: dict
    ) -> None:
        """Test partial RAG config updates."""
        workspace_id = test_workspace["id"]

        # Create initial RAG config
        create_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Update only chunk_size
        update_data = {"chunk_size": 1500}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

        # Verify the update
        response = client.get(
            f"/api/workspaces/{workspace_id}/rag-config",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["chunk_size"] == 1500
        assert data["chunk_overlap"] == 200  # Should remain unchanged

        # Update multiple fields
        update_data = {"chunk_overlap": 300, "top_k": 10}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

        # Verify the updates
        response = client.get(
            f"/api/workspaces/{workspace_id}/rag-config",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["chunk_overlap"] == 300
        assert data["top_k"] == 10
        assert data["chunk_size"] == 1500  # Should remain unchanged

    def test_rag_config_empty_update(
        self, client: Any, auth_token: str, test_workspace: dict
    ) -> None:
        """Test empty RAG config update."""
        workspace_id = test_workspace["id"]

        # Create initial RAG config
        create_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Try empty update
        update_data: dict = {}
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test chunk_size too small
        invalid_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 50,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test chunk_size too large
        invalid_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 6000,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test chunk_overlap negative
        invalid_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": -10,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test top_k too small
        invalid_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "top_k": 0,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400

        # Test top_k too large
        invalid_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "top_k": 100,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400
