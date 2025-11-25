"""Unit tests for authentication routes."""

import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from jwt.exceptions import InvalidTokenError
from shared.models import User
from shared.repositories import DefaultRagConfigRepository

from src.domains.auth.exceptions import UserAlreadyExistsError, UserAuthenticationError
from src.domains.auth.routes import auth_bp


@pytest.fixture
def app() -> Flask:
    """Create a test Flask app."""
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app: Flask):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def mock_user_service():
    """Mock user service."""
    return Mock()


@pytest.fixture
def mock_default_rag_config_repository():
    """Mock default RAG config repository."""
    return Mock(spec=DefaultRagConfigRepository)


@pytest.fixture
def mock_app_context(mock_user_service, mock_default_rag_config_repository):
    """Mock app context."""
    mock_context = Mock()
    mock_context.user_service = mock_user_service
    mock_context.default_rag_config_repository = mock_default_rag_config_repository
    return mock_context


@pytest.fixture
def sample_user():
    """Create a sample user."""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="",
        full_name="Test User",
        theme_preference="dark",
        created_at=None,
        updated_at=None,
    )
    user.set_password("password123")
    return user


class TestSignupEndpoint:
    """Tests for user signup endpoint."""

    def test_signup_success(self, client, mock_app_context, sample_user):
        """Test successful user signup."""
        mock_app_context.user_service.register_user.return_value = sample_user

        with (
            patch("src.domains.auth.routes.g") as mock_g,
            patch("src.domains.auth.routes.create_access_token") as mock_create_token,
        ):

            mock_g.app_context = mock_app_context
            mock_create_token.return_value = "jwt_token"

            response = client.post(
                "/api/auth/signup",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "password123",
                    "full_name": "Test User",
                },
            )

            assert response.status_code == 201
            data = json.loads(response.data)

            expected_response = {
                "access_token": "jwt_token",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "created_at": None,
                    "theme_preference": "dark",
                },
            }

            assert data == expected_response
            mock_app_context.user_service.register_user.assert_called_once_with(
                username="testuser",
                email="test@example.com",
                password="password123",
                full_name="Test User",
            )

    def test_signup_missing_required_fields(self, client):
        """Test signup with missing required fields."""
        response = client.post(
            "/api/auth/signup", json={"username": "testuser"}  # Missing email and password
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "username, email, and password are required" in data["error"]

    def test_signup_password_too_short(self, client):
        """Test signup with password too short."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "12345",  # Too short
            },
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Password must be at least 6 characters" in data["error"]

    def test_signup_user_already_exists(self, client, mock_app_context):
        """Test signup when user already exists."""
        mock_app_context.user_service.register_user.side_effect = UserAlreadyExistsError(
            "Username already exists"
        )

        with patch("src.domains.auth.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/auth/signup",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "password123",
                },
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["error"] == "Username already exists"

    def test_signup_invalid_json(self, client):
        """Test signup with invalid JSON."""
        response = client.post(
            "/api/auth/signup", data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Request body is required" in data["error"]


class TestLoginEndpoint:
    """Tests for user login endpoint."""

    def test_login_success(self, client, mock_app_context, sample_user):
        """Test successful user login."""
        mock_app_context.user_service.authenticate_user.return_value = sample_user

        with (
            patch("src.domains.auth.routes.g") as mock_g,
            patch("src.domains.auth.routes.create_access_token") as mock_create_token,
        ):

            mock_g.app_context = mock_app_context
            mock_create_token.return_value = "jwt_token"

            response = client.post(
                "/api/auth/login", json={"username": "testuser", "password": "password123"}
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            expected_response = {
                "access_token": "jwt_token",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "created_at": None,
                    "theme_preference": "dark",
                },
            }

            assert data == expected_response
            mock_app_context.user_service.authenticate_user.assert_called_once_with(
                username="testuser", password="password123"
            )

    def test_login_missing_required_fields(self, client):
        """Test login with missing required fields."""
        response = client.post("/api/auth/login", json={"username": "testuser"})  # Missing password

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "username and password are required" in data["error"]

    def test_login_invalid_credentials(self, client, mock_app_context):
        """Test login with invalid credentials."""
        mock_app_context.user_service.authenticate_user.side_effect = UserAuthenticationError(
            "Invalid credentials"
        )

        with patch("src.domains.auth.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/auth/login", json={"username": "testuser", "password": "wrongpassword"}
            )

            assert response.status_code == 401
            data = json.loads(response.data)
            assert data["error"] == "Invalid credentials"

    def test_login_invalid_json(self, client):
        """Test login with invalid JSON."""
        response = client.post(
            "/api/auth/login", data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Request body is required" in data["error"]


class TestGetMeEndpoint:
    """Tests for get current user endpoint."""

    def test_get_me_success(self, client, sample_user):
        """Test successful get current user."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = sample_user

            response = client.get("/api/auth/me")

            assert response.status_code == 200
            data = json.loads(response.data)

            expected_response = {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "created_at": None,
                "theme_preference": "dark",
            }

            assert data == expected_response

    def test_get_me_invalid_token(self, client):
        """Test get current user with invalid token."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.side_effect = InvalidTokenError("Invalid token")

            response = client.get("/api/auth/me")

            assert response.status_code == 401
            data = json.loads(response.data)
            assert "Invalid token" in data["error"]


class TestLogoutEndpoint:
    """Tests for logout endpoint."""

    def test_logout_success(self, client):
        """Test successful logout."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Successfully logged out"


class TestChangePasswordEndpoint:
    """Tests for change password endpoint."""

    def test_change_password_success(self, client, sample_user):
        """Test successful password change."""
        with (
            patch("src.domains.auth.routes.get_current_user") as mock_get_current_user,
            patch("src.domains.auth.routes.g") as mock_g,
        ):

            mock_get_current_user.return_value = sample_user
            mock_app_context = Mock()
            mock_app_context.user_service.update_user.return_value = sample_user
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/auth/change-password",
                json={"current_password": "password123", "new_password": "newpassword123"},
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["message"] == "Password changed successfully"

    def test_change_password_missing_fields(self, client):
        """Test change password with missing fields."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = Mock()

            response = client.post(
                "/api/auth/change-password",
                json={"current_password": "password123"},  # Missing new_password
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "current_password and new_password are required" in data["error"]

    def test_change_password_wrong_current_password(self, client, sample_user):
        """Test change password with wrong current password."""
        sample_user.set_password("different_password")  # Set different password

        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = sample_user

            response = client.post(
                "/api/auth/change-password",
                json={
                    "current_password": "password123",  # Wrong current password
                    "new_password": "newpassword123",
                },
            )

            assert response.status_code == 401
            data = json.loads(response.data)
            assert data["error"] == "Current password is incorrect"

    def test_change_password_new_password_too_short(self, client, sample_user):
        """Test change password with new password too short."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = sample_user

            response = client.post(
                "/api/auth/change-password",
                json={"current_password": "password123", "new_password": "12345"},  # Too short
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "New password must be at least 6 characters" in data["error"]


class TestUpdateProfileEndpoint:
    """Tests for update profile endpoint."""

    def test_update_profile_success(self, client, sample_user, mock_app_context):
        """Test successful profile update."""
        updated_user = User(
            id=1,
            username="testuser",
            email="newemail@example.com",
            password_hash="",
            full_name="Updated Name",
            theme_preference="dark",
            created_at=None,
            updated_at=None,
        )

        with (
            patch("src.domains.auth.routes.get_current_user") as mock_get_current_user,
            patch("src.domains.auth.routes.g") as mock_g,
        ):

            mock_get_current_user.return_value = sample_user
            mock_app_context.user_service.update_user.return_value = updated_user
            mock_g.app_context = mock_app_context

            response = client.patch(
                "/api/auth/profile",
                json={"full_name": "Updated Name", "email": "newemail@example.com"},
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            expected_response = {
                "id": 1,
                "username": "testuser",
                "email": "newemail@example.com",
                "full_name": "Updated Name",
                "created_at": None,
                "theme_preference": "dark",
            }

            assert data == expected_response

    def test_update_profile_invalid_email(self, client, sample_user):
        """Test profile update with invalid email."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = sample_user

            response = client.patch(
                "/api/auth/profile", json={"email": "invalid-email"}  # Invalid email format
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["error"] == "Invalid email format"

    def test_update_profile_invalid_json(self, client):
        """Test profile update with invalid JSON."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = Mock()

            response = client.patch(
                "/api/auth/profile", data="invalid json", content_type="application/json"
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "Request body is required" in data["error"]


class TestUpdatePreferencesEndpoint:
    """Tests for update preferences endpoint."""

    def test_update_preferences_success(self, client, sample_user, mock_app_context):
        """Test successful preferences update."""
        updated_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="",
            full_name="Test User",
            theme_preference="light",
            created_at=None,
            updated_at=None,
        )

        with (
            patch("src.domains.auth.routes.get_current_user") as mock_get_current_user,
            patch("src.domains.auth.routes.g") as mock_g,
        ):

            mock_get_current_user.return_value = sample_user
            mock_app_context.user_service.update_user.return_value = updated_user
            mock_g.app_context = mock_app_context

            response = client.patch("/api/auth/preferences", json={"theme_preference": "light"})

            assert response.status_code == 200
            data = json.loads(response.data)

            expected_response = {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "created_at": None,
                "theme_preference": "light",
            }

            assert data == expected_response

    def test_update_preferences_invalid_theme(self, client, sample_user):
        """Test preferences update with invalid theme."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = sample_user

            response = client.patch(
                "/api/auth/preferences", json={"theme_preference": "invalid"}  # Invalid theme
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["error"] == "theme_preference must be 'light' or 'dark'"


class TestDefaultRagConfigEndpoints:
    """Tests for default RAG config endpoints."""

    def test_get_default_rag_config_success(self, client, mock_app_context):
        """Test successful get default RAG config."""
        from datetime import datetime

        from shared.models.default_rag_config import DefaultRagConfig

        config = DefaultRagConfig(
            id=1,
            user_id=1,
            embedding_model="nomic-embed-text",
            embedding_dim=None,
            retriever_type="vector",
            chunk_size=1000,
            chunk_overlap=200,
            top_k=8,
            rerank_enabled=False,
            rerank_model=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_app_context.default_rag_config_repository.get_by_user_id.return_value = config

        with (
            patch("src.domains.auth.routes.get_current_user") as mock_get_current_user,
            patch("src.domains.auth.routes.g") as mock_g,
        ):

            mock_get_current_user.return_value = Mock(id=1)
            mock_g.app_context = mock_app_context

            response = client.get("/api/auth/default-rag-config")

            assert response.status_code == 200
            data = json.loads(response.data)

            expected_response = {
                "id": 1,
                "user_id": 1,
                "embedding_model": "nomic-embed-text",
                "embedding_dim": None,
                "retriever_type": "vector",
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "top_k": 8,
                "rerank_enabled": False,
                "rerank_model": None,
            }

            assert data == expected_response

    def test_get_default_rag_config_not_found(self, client, mock_app_context):
        """Test get default RAG config when not found."""
        mock_app_context.default_rag_config_repository.get_by_user_id.return_value = None

        with (
            patch("src.domains.auth.routes.get_current_user") as mock_get_current_user,
            patch("src.domains.auth.routes.g") as mock_g,
        ):

            mock_get_current_user.return_value = Mock(id=1)
            mock_g.app_context = mock_app_context

            response = client.get("/api/auth/default-rag-config")

            assert response.status_code == 404
            data = json.loads(response.data)
            assert data["error"] == "Default RAG configuration not found"

    def test_update_default_rag_config_success(self, client, mock_app_context):
        """Test successful update default RAG config."""
        from datetime import datetime

        from shared.models.default_rag_config import DefaultRagConfig

        config = DefaultRagConfig(
            id=1,
            user_id=1,
            embedding_model="new-model",
            embedding_dim=768,
            retriever_type="vector",
            chunk_size=1500,
            chunk_overlap=300,
            top_k=10,
            rerank_enabled=True,
            rerank_model="rerank-model",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        mock_app_context.default_rag_config_repository.upsert.return_value = config

        with (
            patch("src.domains.auth.routes.get_current_user") as mock_get_current_user,
            patch("src.domains.auth.routes.g") as mock_g,
        ):

            mock_get_current_user.return_value = Mock(id=1)
            mock_g.app_context = mock_app_context

            response = client.put(
                "/api/auth/default-rag-config",
                json={
                    "embedding_model": "new-model",
                    "embedding_dim": 768,
                    "retriever_type": "vector",
                    "chunk_size": 1500,
                    "chunk_overlap": 300,
                    "top_k": 10,
                    "rerank_enabled": True,
                    "rerank_model": "rerank-model",
                },
            )

            assert response.status_code == 200
            data = json.loads(response.data)

            expected_response = {
                "id": 1,
                "user_id": 1,
                "embedding_model": "new-model",
                "embedding_dim": 768,
                "retriever_type": "vector",
                "chunk_size": 1500,
                "chunk_overlap": 300,
                "top_k": 10,
                "rerank_enabled": True,
                "rerank_model": "rerank-model",
            }

            assert data == expected_response

    def test_update_default_rag_config_invalid_retriever_type(self, client):
        """Test update default RAG config with invalid retriever type."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = Mock(id=1)

            response = client.put(
                "/api/auth/default-rag-config",
                json={"retriever_type": "invalid"},  # Invalid retriever type
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["error"] == "retriever_type must be 'vector', 'graph', or 'hybrid'"

    def test_update_default_rag_config_chunk_size_too_small(self, client):
        """Test update default RAG config with chunk size too small."""
        with patch("src.domains.auth.routes.get_current_user") as mock_get_current_user:
            mock_get_current_user.return_value = Mock(id=1)

            response = client.put(
                "/api/auth/default-rag-config", json={"chunk_size": 50}  # Too small
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "chunk_size must be between 100 and 5000" in data["error"]
