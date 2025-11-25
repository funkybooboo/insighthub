"""Integration tests for RAG config functionality."""


class TestRagConfigIntegration:
    """Integration tests for RAG config CRUD operations."""

    def test_full_rag_config_lifecycle(self, client, auth_token, test_workspace) -> None:
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

    def test_create_duplicate_rag_config(self, client, auth_token, test_workspace) -> None:
        """Test that creating duplicate RAG config fails."""
        workspace_id = test_workspace["id"]

        # Create first config
        create_data = {"embedding_model": "nomic-embed-text", "chunk_size": 1000}
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Try to create second config - should fail
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 409
        error_data = response.get_json()
        assert "already exists" in error_data["error"]

    def test_rag_config_validation(self, client, auth_token, test_workspace) -> None:
        """Test RAG config validation rules."""
        workspace_id = test_workspace["id"]

        # Test invalid retriever_type
        invalid_data = {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "invalid_type",
            "chunk_size": 1000,
        }
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=invalid_data,
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

    def test_rag_config_access_control(self, client, auth_token, test_workspace) -> None:
        """Test that RAG config operations respect workspace access control."""
        # Test accessing non-existent workspace
        response = client.get(
            "/api/workspaces/99999/rag-config", headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404

        # Test creating config for non-existent workspace
        create_data = {"embedding_model": "nomic-embed-text", "chunk_size": 1000}
        response = client.post(
            "/api/workspaces/99999/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400  # Should fail due to workspace validation

    def test_rag_config_update_validation(self, client, auth_token, test_workspace) -> None:
        """Test RAG config update validation."""
        workspace_id = test_workspace["id"]

        # First create a config
        create_data = {"embedding_model": "nomic-embed-text", "chunk_size": 1000}
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Test updating with invalid data
        invalid_updates = [
            {"retriever_type": "invalid"},
            {"chunk_size": 50},
            {"chunk_size": 6000},
            {"chunk_overlap": -10},
            {"top_k": 0},
            {"top_k": 100},
        ]

        for invalid_update in invalid_updates:
            response = client.patch(
                f"/api/workspaces/{workspace_id}/rag-config",
                json=invalid_update,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert response.status_code == 400, f"Should reject invalid update: {invalid_update}"

    def test_rag_config_partial_updates(self, client, auth_token, test_workspace) -> None:
        """Test that RAG config supports partial updates."""
        workspace_id = test_workspace["id"]

        # Create initial config
        create_data = {"embedding_model": "nomic-embed-text", "chunk_size": 1000, "top_k": 8}
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Update only chunk_size
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json={"chunk_size": 1200},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["chunk_size"] == 1200
        assert data["top_k"] == 8  # Should remain unchanged

        # Update only top_k
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json={"top_k": 12},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["chunk_size"] == 1200  # Should remain unchanged
        assert data["top_k"] == 12

    def test_rag_config_empty_update(self, client, auth_token, test_workspace) -> None:
        """Test that empty updates are handled gracefully."""
        workspace_id = test_workspace["id"]

        # Create initial config
        create_data = {"embedding_model": "nomic-embed-text", "chunk_size": 1000}
        response = client.post(
            f"/api/workspaces/{workspace_id}/rag-config",
            json=create_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 201

        # Try empty update
        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json={},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 400
        error_data = response.get_json()
        assert "error" in error_data
