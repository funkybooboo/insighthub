"""Integration tests for workspace API endpoints."""

import json

from flask.testing import FlaskClient


class TestWorkspaceCreateEndpoint:
    """Tests for POST /api/workspaces endpoint."""

    def test_create_workspace_returns_201(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/workspaces returns 201 with workspace data."""
        response = client.post(
            "/api/workspaces",
            json={"name": "Test Workspace", "description": "A test workspace"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "Test Workspace"
        assert data["description"] == "A test workspace"
        assert "id" in data
        assert data["status"] == "provisioning"

    def test_create_workspace_with_rag_config(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/workspaces with RAG config returns workspace with config."""
        response = client.post(
            "/api/workspaces",
            json={
                "name": "RAG Workspace",
                "rag_config": {
                    "retriever_type": "hybrid",
                    "chunk_size": 500,
                    "top_k": 10,
                },
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["rag_config"]["retriever_type"] == "hybrid"
        assert data["rag_config"]["chunk_size"] == 500
        assert data["rag_config"]["top_k"] == 10

    def test_create_workspace_missing_name_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/workspaces without name returns 400."""
        response = client.post(
            "/api/workspaces",
            json={"description": "No name"},
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_create_workspace_empty_name_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/workspaces with empty name returns 400."""
        response = client.post(
            "/api/workspaces",
            json={"name": ""},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_workspace_name_too_long_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/workspaces with name > 100 chars returns 400."""
        response = client.post(
            "/api/workspaces",
            json={"name": "A" * 101},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_workspace_unauthorized_returns_401(self, client: FlaskClient) -> None:
        """POST /api/workspaces without auth returns 401."""
        response = client.post(
            "/api/workspaces",
            json={"name": "Test"},
        )

        assert response.status_code == 401


class TestWorkspaceListEndpoint:
    """Tests for GET /api/workspaces endpoint."""

    def test_list_workspaces_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces returns 200 with list."""
        response = client.get("/api/workspaces", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_list_workspaces_returns_created_workspaces(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces returns previously created workspaces."""
        # Create workspaces
        client.post(
            "/api/workspaces",
            json={"name": "Workspace 1"},
            headers=auth_headers,
        )
        client.post(
            "/api/workspaces",
            json={"name": "Workspace 2"},
            headers=auth_headers,
        )

        response = client.get("/api/workspaces", headers=auth_headers)

        data = json.loads(response.data)
        assert len(data) >= 2
        names = [ws["name"] for ws in data]
        assert "Workspace 1" in names
        assert "Workspace 2" in names

    def test_list_workspaces_includes_stats(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces includes document_count and session_count."""
        client.post(
            "/api/workspaces",
            json={"name": "Stats Test"},
            headers=auth_headers,
        )

        response = client.get("/api/workspaces", headers=auth_headers)

        data = json.loads(response.data)
        assert len(data) >= 1
        ws = next(w for w in data if w["name"] == "Stats Test")
        assert "document_count" in ws
        assert "session_count" in ws

    def test_list_workspaces_unauthorized_returns_401(self, client: FlaskClient) -> None:
        """GET /api/workspaces without auth returns 401."""
        response = client.get("/api/workspaces")

        assert response.status_code == 401


class TestWorkspaceGetEndpoint:
    """Tests for GET /api/workspaces/<id> endpoint."""

    def test_get_workspace_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces/<id> returns 200 with workspace."""
        # Create workspace
        create_response = client.post(
            "/api/workspaces",
            json={"name": "Get Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.get(f"/api/workspaces/{workspace_id}", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == workspace_id
        assert data["name"] == "Get Test"

    def test_get_workspace_includes_rag_config(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces/<id> includes rag_config."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "Config Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.get(f"/api/workspaces/{workspace_id}", headers=auth_headers)

        data = json.loads(response.data)
        assert "rag_config" in data
        assert "embedding_model" in data["rag_config"]

    def test_get_workspace_not_found_returns_404(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces/<id> for nonexistent returns 404."""
        response = client.get("/api/workspaces/99999", headers=auth_headers)

        assert response.status_code == 404


class TestWorkspaceUpdateEndpoint:
    """Tests for PUT/PATCH /api/workspaces/<id> endpoint."""

    def test_update_workspace_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PATCH /api/workspaces/<id> returns 200 with updated workspace."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "Original Name"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.patch(
            f"/api/workspaces/{workspace_id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Updated Name"

    def test_update_workspace_put_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PUT /api/workspaces/<id> returns 200 with updated workspace."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "Original"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.put(
            f"/api/workspaces/{workspace_id}",
            json={"name": "Updated", "description": "New desc"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Updated"
        assert data["description"] == "New desc"

    def test_update_workspace_not_found_returns_404(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PATCH /api/workspaces/<id> for nonexistent returns 404."""
        response = client.patch(
            "/api/workspaces/99999",
            json={"name": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_workspace_no_fields_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PATCH /api/workspaces/<id> with no valid fields returns 400."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.patch(
            f"/api/workspaces/{workspace_id}",
            json={"invalid_field": "value"},
            headers=auth_headers,
        )

        assert response.status_code == 400


class TestWorkspaceDeleteEndpoint:
    """Tests for DELETE /api/workspaces/<id> endpoint."""

    def test_delete_workspace_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """DELETE /api/workspaces/<id> returns 200."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "To Delete"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.delete(f"/api/workspaces/{workspace_id}", headers=auth_headers)

        assert response.status_code == 200

    def test_delete_workspace_removes_workspace(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """DELETE /api/workspaces/<id> removes the workspace."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "To Delete"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        client.delete(f"/api/workspaces/{workspace_id}", headers=auth_headers)

        get_response = client.get(f"/api/workspaces/{workspace_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_workspace_not_found_returns_404(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """DELETE /api/workspaces/<id> for nonexistent returns 404."""
        response = client.delete("/api/workspaces/99999", headers=auth_headers)

        assert response.status_code == 404


class TestWorkspaceStatsEndpoint:
    """Tests for GET /api/workspaces/<id>/stats endpoint."""

    def test_get_stats_returns_200(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """GET /api/workspaces/<id>/stats returns 200 with stats."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "Stats Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.get(f"/api/workspaces/{workspace_id}/stats", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "workspace_id" in data
        assert "document_count" in data
        assert "chat_session_count" in data

    def test_get_stats_not_found_returns_404(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces/<id>/stats for nonexistent returns 404."""
        response = client.get("/api/workspaces/99999/stats", headers=auth_headers)

        assert response.status_code == 404


class TestRagConfigEndpoints:
    """Tests for RAG config endpoints."""

    def test_get_rag_config_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces/<id>/rag-config returns 200."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "RAG Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.get(f"/api/workspaces/{workspace_id}/rag-config", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "embedding_model" in data
        assert "retriever_type" in data

    def test_update_rag_config_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PATCH /api/workspaces/<id>/rag-config returns 200."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "RAG Update Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json={"retriever_type": "graph", "top_k": 15},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["retriever_type"] == "graph"
        assert data["top_k"] == 15

    def test_update_rag_config_invalid_retriever_type_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PATCH /api/workspaces/<id>/rag-config with invalid retriever_type returns 400."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "RAG Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json={"retriever_type": "invalid"},
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_update_rag_config_invalid_chunk_size_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PATCH /api/workspaces/<id>/rag-config with invalid chunk_size returns 400."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "RAG Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json={"chunk_size": 50},  # Below minimum of 100
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_update_rag_config_invalid_top_k_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """PATCH /api/workspaces/<id>/rag-config with invalid top_k returns 400."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "RAG Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.patch(
            f"/api/workspaces/{workspace_id}/rag-config",
            json={"top_k": 100},  # Above maximum of 50
            headers=auth_headers,
        )

        assert response.status_code == 400


class TestValidateAccessEndpoint:
    """Tests for GET /api/workspaces/<id>/validate-access endpoint."""

    def test_validate_access_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces/<id>/validate-access returns 200."""
        create_response = client.post(
            "/api/workspaces",
            json={"name": "Access Test"},
            headers=auth_headers,
        )
        workspace_id = json.loads(create_response.data)["id"]

        response = client.get(
            f"/api/workspaces/{workspace_id}/validate-access", headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["has_access"] is True
        assert data["workspace_id"] == str(workspace_id)

    def test_validate_access_nonexistent_returns_false(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/workspaces/<id>/validate-access for nonexistent returns has_access=false."""
        response = client.get("/api/workspaces/99999/validate-access", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["has_access"] is False
