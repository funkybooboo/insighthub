"""Integration tests for health endpoints."""

from flask.testing import FlaskClient


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""

    def test_health_endpoint_success(self, client: FlaskClient) -> None:
        """Test basic health endpoint returns success."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "timestamp" in data
        assert "version" in data
        assert "checks" in data

    def test_readiness_endpoint_success(self, client: FlaskClient) -> None:
        """Test readiness endpoint returns success."""
        response = client.get("/ready")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "ready"

    def test_liveness_endpoint_success(self, client: FlaskClient) -> None:
        """Test liveness endpoint returns success."""
        response = client.get("/live")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "alive"

    def test_metrics_endpoint_success(self, client: FlaskClient) -> None:
        """Test metrics endpoint returns data."""
        response = client.get("/metrics")
        assert response.status_code == 200

        data = response.get_json()
        assert "status" in data
        assert "uptime" in data
        assert "memory_usage" in data
        assert "active_connections" in data

    def test_api_docs_endpoint_success(self, client: FlaskClient) -> None:
        """Test API documentation endpoint returns OpenAPI spec."""
        response = client.get("/docs")
        assert response.status_code == 200

        data = response.get_json()
        assert data["openapi"] == "3.0.3"
        assert "info" in data
        assert "title" in data["info"]
        assert "paths" in data
        assert "components" in data

    def test_health_endpoint_includes_expected_checks(self, client: FlaskClient) -> None:
        """Test health endpoint includes expected health checks."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.get_json()
        checks = data["checks"]

        # Should include database check
        assert "database" in checks

        # Should include RAG system check
        assert "rag_system" in checks

        # Should include message queue check
        assert "message_queue" in checks

        # Should include LLM service check
        assert "llm_service" in checks

    def test_health_endpoint_check_structure(self, client: FlaskClient) -> None:
        """Test health check responses have proper structure."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.get_json()
        checks = data["checks"]

        for _check_name, check_data in checks.items():
            assert "status" in check_data
            assert check_data["status"] in ["healthy", "unhealthy", "warning"]
            assert "message" in check_data

    def test_health_endpoint_correlation_id_header(self, client: FlaskClient) -> None:
        """Test health endpoints include correlation ID headers."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        correlation_id = response.headers["X-Request-ID"]
        assert len(correlation_id) > 0

    def test_health_endpoints_not_rate_limited(self, client: FlaskClient) -> None:
        """Test health endpoints are exempt from rate limiting."""
        # Make multiple requests to health endpoints
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

            response = client.get("/ready")
            assert response.status_code == 200

            response = client.get("/live")
            assert response.status_code == 200
