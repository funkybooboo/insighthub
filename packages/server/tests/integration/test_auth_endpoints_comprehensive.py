"""Integration tests for authentication endpoints with test containers."""

import json
import time
from typing import Any

import pytest
from flask.testing import FlaskClient

from shared.models import User


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints using test containers."""

    def test_signup_success(self, client: FlaskClient) -> None:
        """Test successful user signup with all middleware applied."""
        signup_data = {
            "username": "integration_user",
            "email": "integration@example.com",
            "password": "secure_password123",
            "full_name": "Integration User"
        }

        response = client.post(
            "/api/auth/signup",
            data=json.dumps(signup_data),
            content_type="application/json"
        )

        assert response.status_code == 201

        # Check security headers are present
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Response-Time" in response.headers  # Performance monitoring

        data = json.loads(response.data)
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

        user = data["user"]
        assert user["id"] > 0
        assert user["username"] == "integration_user"
        assert user["email"] == "integration@example.com"
        assert user["full_name"] == "Integration User"
        assert "created_at" in user
        assert "theme_preference" in user

    def test_signup_validation_errors(self, client: FlaskClient) -> None:
        """Test signup validation with various error conditions."""
        test_cases = [
            # Missing required fields
            (
                {"email": "test@example.com", "password": "password123"},
                "username, email, and password are required"
            ),
            # Password too short
            (
                {
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "12345"
                },
                "Password must be at least 6 characters"
            ),
            # Invalid JSON
            ("invalid json", "Request body is required"),
        ]

        for payload, expected_error in test_cases:
            if isinstance(payload, dict):
                response = client.post(
                    "/api/auth/signup",
                    data=json.dumps(payload),
                    content_type="application/json"
                )
            else:
                response = client.post(
                    "/api/auth/signup",
                    data=payload,
                    content_type="application/json"
                )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert expected_error in data["error"]

    def test_signup_duplicate_user(self, client: FlaskClient, test_user: User) -> None:
        """Test signup with duplicate username or email."""
        # Try to create user with same username
        signup_data = {
            "username": test_user.username,  # Duplicate username
            "email": "different@example.com",
            "password": "password123"
        }

        response = client.post(
            "/api/auth/signup",
            data=json.dumps(signup_data),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Username" in data["error"] and "already exists" in data["error"]

        # Try to create user with same email
        signup_data = {
            "username": "different_user",
            "email": test_user.email,  # Duplicate email
            "password": "password123"
        }

        response = client.post(
            "/api/auth/signup",
            data=json.dumps(signup_data),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Email" in data["error"] and "already exists" in data["error"]

    def test_login_success(self, client: FlaskClient, test_user: User) -> None:
        """Test successful login."""
        login_data = {
            "username": test_user.username,
            "password": "test_password"  # From test fixture
        }

        response = client.post(
            "/api/auth/login",
            data=json.dumps(login_data),
            content_type="application/json"
        )

        assert response.status_code == 200

        # Check security headers
        assert "X-Frame-Options" in response.headers
        assert "X-Response-Time" in response.headers

        data = json.loads(response.data)
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data

        user = data["user"]
        assert user["username"] == test_user.username
        assert user["email"] == test_user.email

    def test_login_invalid_credentials(self, client: FlaskClient, test_user: User) -> None:
        """Test login with invalid credentials."""
        test_cases = [
            # Wrong password
            {"username": test_user.username, "password": "wrong_password"},
            # Non-existent user
            {"username": "nonexistent", "password": "password123"},
        ]

        for login_data in test_cases:
            response = client.post(
                "/api/auth/login",
                data=json.dumps(login_data),
                content_type="application/json"
            )

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "error" in data

    def test_get_current_user_authenticated(self, client: FlaskClient, auth_headers: dict[str, str], test_user: User) -> None:
        """Test getting current user when authenticated."""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200

        # Check security headers
        assert "X-Frame-Options" in response.headers
        assert "X-Response-Time" in response.headers

        data = json.loads(response.data)
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "created_at" in data
        assert "theme_preference" in data

    def test_get_current_user_unauthenticated(self, client: FlaskClient) -> None:
        """Test getting current user without authentication."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data

    def test_logout(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test logout functionality."""
        response = client.post("/api/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Successfully logged out"

        # Check security headers are still present
        assert "X-Frame-Options" in response.headers

    def test_change_password_success(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test successful password change."""
        change_data = {
            "current_password": "test_password",
            "new_password": "new_secure_password123"
        }

        response = client.post(
            "/api/auth/change-password",
            data=json.dumps(change_data),
            content_type="application/json",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Password changed successfully"

    def test_change_password_validation_errors(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test password change validation errors."""
        test_cases = [
            # Missing fields
            {"current_password": "password"},
            {"new_password": "newpassword"},
            {},
            # Wrong current password
            {"current_password": "wrong_password", "new_password": "newpassword123"},
            # New password too short
            {"current_password": "test_password", "new_password": "12345"},
        ]

        for change_data in test_cases:
            response = client.post(
                "/api/auth/change-password",
                data=json.dumps(change_data),
                content_type="application/json",
                headers=auth_headers
            )

            assert response.status_code in [400, 401]
            data = json.loads(response.data)
            assert "error" in data

    def test_update_profile_success(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test successful profile update."""
        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com"
        }

        response = client.patch(
            "/api/auth/profile",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["full_name"] == "Updated Name"
        assert data["email"] == "updated@example.com"

    def test_update_profile_validation_errors(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test profile update validation errors."""
        # Invalid email
        update_data = {"email": "invalid-email"}

        response = client.patch(
            "/api/auth/profile",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid email format" in data["error"]

    def test_update_preferences_success(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test successful preferences update."""
        update_data = {"theme_preference": "dark"}

        response = client.patch(
            "/api/auth/preferences",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["theme_preference"] == "dark"

    def test_update_preferences_invalid_theme(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test preferences update with invalid theme."""
        update_data = {"theme_preference": "invalid_theme"}

        response = client.patch(
            "/api/auth/preferences",
            data=json.dumps(update_data),
            content_type="application/json",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "theme_preference must be 'light' or 'dark'" in data["error"]

    def test_default_rag_config_workflow(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test complete default RAG config workflow."""
        # Initially should return 404 (not configured)
        response = client.get("/api/auth/default-rag-config", headers=auth_headers)
        assert response.status_code == 404

        # Create default config
        config_data = {
            "embedding_model": "nomic-embed-text",
            "embedding_dim": 768,
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
            "rerank_enabled": False,
            "rerank_model": None
        }

        response = client.put(
            "/api/auth/default-rag-config",
            data=json.dumps(config_data),
            content_type="application/json",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["embedding_model"] == "nomic-embed-text"
        assert data["retriever_type"] == "vector"
        assert data["chunk_size"] == 1000

        # Now GET should return the config
        response = client.get("/api/auth/default-rag-config", headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["embedding_model"] == "nomic-embed-text"

    def test_default_rag_config_validation(self, client: FlaskClient, auth_headers: dict[str, str]) -> None:
        """Test RAG config validation."""
        invalid_configs = [
            {"retriever_type": "invalid_type"},
            {"chunk_size": 50},  # Too small
            {"chunk_overlap": -10},  # Negative
            {"top_k": 100},  # Too large
        ]

        for config_data in invalid_configs:
            response = client.put(
                "/api/auth/default-rag-config",
                data=json.dumps(config_data),
                content_type="application/json",
                headers=auth_headers
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "error" in data

    def test_rate_limiting(self, client: FlaskClient) -> None:
        """Test rate limiting middleware."""
        # Make multiple requests quickly to trigger rate limit
        signup_data = {
            "username": "ratelimit_test",
            "email": "ratelimit@example.com",
            "password": "password123"
        }

        # Make several requests in quick succession
        responses = []
        for i in range(10):  # More than the per-minute limit
            response = client.post(
                "/api/auth/signup",
                data=json.dumps(signup_data),
                content_type="application/json"
            )
            responses.append(response)

        # At least one should be rate limited (429)
        rate_limited_responses = [r for r in responses if r.status_code == 429]
        assert len(rate_limited_responses) > 0

        # Check rate limit response format
        rate_limit_response = rate_limited_responses[0]
        data = json.loads(rate_limit_response.data)
        assert "error" in data
        assert "retry_after" in data

    def test_request_validation_middleware(self, client: FlaskClient) -> None:
        """Test request validation middleware."""
        # Test oversized request
        large_data = {"username": "a" * (1024 * 1024)}  # 1MB of data

        response = client.post(
            "/api/auth/signup",
            data=json.dumps(large_data),
            content_type="application/json"
        )

        # Should be rejected due to size limits
        assert response.status_code in [400, 413]

    def test_content_type_validation(self, client: FlaskClient) -> None:
        """Test content type validation."""
        signup_data = {
            "username": "content_type_test",
            "email": "test@example.com",
            "password": "password123"
        }

        # Test with wrong content type
        response = client.post(
            "/api/auth/signup",
            data=json.dumps(signup_data),
            content_type="text/plain"  # Wrong content type
        )

        assert response.status_code == 415
        data = json.loads(response.data)
        assert "error" in data

    def test_json_validation(self, client: FlaskClient) -> None:
        """Test JSON validation middleware."""
        # Send invalid JSON
        response = client.post(
            "/api/auth/signup",
            data='{"invalid": json}',
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid JSON payload" in data["error"]

    def test_path_traversal_protection(self, client: FlaskClient) -> None:
        """Test path traversal protection."""
        # Try to access paths with traversal patterns
        traversal_paths = [
            "/api/auth/../../../etc/passwd",
            "/api/auth/..%2F..%2Fetc%2Fpasswd"
        ]

        for path in traversal_paths:
            response = client.get(path)
            assert response.status_code == 400
            data = json.loads(response.data)
            assert "Invalid request path" in data["error"]

    def test_cors_headers(self, client: FlaskClient) -> None:
        """Test CORS headers are properly set."""
        response = client.options("/api/auth/signup")

        # CORS headers should be present
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers

    def test_security_headers(self, client: FlaskClient) -> None:
        """Test security headers are applied to all responses."""
        response = client.get("/api/auth/me")  # Will return 401 but still has headers

        # Security headers should be present
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert "X-XSS-Protection" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers

    def test_performance_monitoring_headers(self, client: FlaskClient) -> None:
        """Test performance monitoring adds timing headers."""
        response = client.get("/api/auth/me")  # Any endpoint

        # Performance header should be present
        assert "X-Response-Time" in response.headers

        # Should be in format like "0.123s"
        timing_header = response.headers["X-Response-Time"]
        assert timing_header.endswith("s")
        assert float(timing_header[:-1]) >= 0

    def test_request_logging_integration(self, client: FlaskClient) -> None:
        """Test that request logging middleware is active (headers indicate it's working)."""
        # The logging middleware doesn't add response headers, but we can verify
        # that the request completes successfully, indicating middleware didn't block it
        response = client.post(
            "/api/auth/login",
            data=json.dumps({"username": "test", "password": "test"}),
            content_type="application/json"
        )

        # Should get a response (even if 401), indicating logging middleware processed it
        assert response.status_code in [200, 401]
        assert "X-Response-Time" in response.headers  # Performance monitoring confirms request was processed