"""Authentication routes."""

from flask import Blueprint, Response, g, jsonify, request
from jwt.exceptions import InvalidTokenError

from .exceptions import UserAlreadyExistsError, UserAuthenticationError
from src.infrastructure.auth import create_access_token, get_current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup() -> tuple[Response, int]:
    """
    Register a new user.

    Request Body:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "full_name": "string" (optional)
        }

    Returns:
        201: {
            "access_token": "string",
            "token_type": "bearer",
            "user": {
                "id": int,
                "username": "string",
                "email": "string",
                "full_name": "string",
                "created_at": "string"
            }
        }
        400: {"error": "string"} - Validation error or user already exists
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    try:
        user = g.app_context.user_service.register_user(
            username=username, email=email, password=password, full_name=full_name
        )
        token = create_access_token(user.id)

        return (
            jsonify(
                {
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "created_at": user.created_at.isoformat(),
                        "theme_preference": user.theme_preference,
                    },
                }
            ),
            201,
        )
    except UserAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login() -> tuple[Response, int]:
    """
    Authenticate a user and return a JWT token.

    Request Body:
        {
            "username": "string",
            "password": "string"
        }

    Returns:
        200: {
            "access_token": "string",
            "token_type": "bearer",
            "user": {
                "id": int,
                "username": "string",
                "email": "string",
                "full_name": "string",
                "created_at": "string"
            }
        }
        401: {"error": "string"} - Invalid credentials
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    try:
        user = g.app_context.user_service.authenticate_user(username=username, password=password)
        token = create_access_token(user.id)

        return (
            jsonify(
                {
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "created_at": user.created_at.isoformat(),
                        "theme_preference": user.theme_preference,
                    },
                }
            ),
            200,
        )
    except UserAuthenticationError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/me", methods=["GET"])
def get_me() -> tuple[Response, int]:
    """
    Get the current authenticated user's information.

    Headers:
        Authorization: Bearer <token>

    Returns:
        200: {
            "id": int,
            "username": "string",
            "email": "string",
            "full_name": "string",
            "created_at": "string"
        }
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        user = get_current_user()
        return (
            jsonify(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat(),
                    "theme_preference": user.theme_preference,
                }
            ),
            200,
        )
    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout() -> tuple[Response, int]:
    """
    Logout endpoint (client-side token removal).

    With stateless JWT, logout is handled client-side by removing the token.
    This endpoint is provided for consistency and future token blacklisting.

    Returns:
        200: {"message": "Successfully logged out"}
    """
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route("/change-password", methods=["POST"])
def change_password() -> tuple[Response, int]:
    """
    Change user password.

    Headers:
        Authorization: Bearer <token>

    Request Body:
        {
            "current_password": "string",
            "new_password": "string"
        }

    Returns:
        200: {"message": "Password changed successfully"}
        400: {"error": "string"} - Invalid request
        401: {"error": "string"} - Invalid credentials or token
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return jsonify({"error": "current_password and new_password are required"}), 400

        if len(new_password) < 6:
            return jsonify({"error": "New password must be at least 6 characters"}), 400

        # Verify current password
        if not user.check_password(current_password):
            return jsonify({"error": "Current password is incorrect"}), 401

        # Update password
        user.set_password(new_password)
        g.app_context.user_service.update_user(user.id)

        return jsonify({"message": "Password changed successfully"}), 200

    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/profile", methods=["PATCH"])
def update_profile() -> tuple[Response, int]:
    """
    Update user profile.

    Headers:
        Authorization: Bearer <token>

    Request Body:
        {
            "full_name": "string",
            "email": "string"
        }

    Returns:
        200: {
            "id": int,
            "username": "string",
            "email": "string",
            "full_name": "string",
            "created_at": "string",
            "theme_preference": "string"
        }
        400: {"error": "string"} - Invalid request
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        full_name = data.get("full_name")
        email = data.get("email")

        # Validate email if provided
        if email and "@" not in email:
            return jsonify({"error": "Invalid email format"}), 400

        # Update user
        updated_user = g.app_context.user_service.update_user(
            user.id, full_name=full_name, email=email
        )

        if not updated_user:
            return jsonify({"error": "Failed to update profile"}), 500

        return (
            jsonify(
                {
                    "id": updated_user.id,
                    "username": updated_user.username,
                    "email": updated_user.email,
                    "full_name": updated_user.full_name,
                    "created_at": updated_user.created_at.isoformat(),
                    "theme_preference": updated_user.theme_preference,
                }
            ),
            200,
        )

    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/preferences", methods=["PATCH"])
def update_preferences() -> tuple[Response, int]:
    """
    Update user preferences.

    Headers:
        Authorization: Bearer <token>

    Request Body:
        {
            "theme_preference": "light" | "dark"
        }

    Returns:
        200: {
            "id": int,
            "username": "string",
            "email": "string",
            "full_name": "string",
            "created_at": "string",
            "theme_preference": "string"
        }
        400: {"error": "string"} - Invalid request
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        theme_preference = data.get("theme_preference")

        if theme_preference and theme_preference not in ["light", "dark"]:
            return jsonify({"error": "theme_preference must be 'light' or 'dark'"}), 400

        if theme_preference:
            updated_user = g.app_context.user_service.update_user(
                user.id, theme_preference=theme_preference
            )
            if not updated_user:
                return jsonify({"error": "Failed to update preferences"}), 500

            return (
                jsonify(
                    {
                        "id": updated_user.id,
                        "username": updated_user.username,
                        "email": updated_user.email,
                        "full_name": updated_user.full_name,
                        "created_at": updated_user.created_at.isoformat(),
                        "theme_preference": updated_user.theme_preference,
                    }
                ),
                200,
            )

        return jsonify({"error": "No valid fields to update"}), 400

    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/default-rag-config", methods=["GET"])
def get_default_rag_config() -> tuple[Response, int]:
    """
    Get user's default RAG configuration.

    Headers:
        Authorization: Bearer <token>

    Returns:
        200: {
            "id": int,
            "user_id": int,
            "embedding_model": "string",
            "embedding_dim": int | null,
            "retriever_type": "string",
            "chunk_size": int,
            "chunk_overlap": int,
            "top_k": int,
            "rerank_enabled": bool,
            "rerank_model": "string" | null
        }
        404: {"error": "Default RAG configuration not found"}
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        user = get_current_user()
        config = g.app_context.default_rag_config_repository.get_by_user_id(user.id)

        if not config:
            return jsonify({"error": "Default RAG configuration not found"}), 404

        return (
            jsonify(
                {
                    "id": config.id,
                    "user_id": config.user_id,
                    "embedding_model": config.embedding_model,
                    "embedding_dim": config.embedding_dim,
                    "retriever_type": config.retriever_type,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_model": config.rerank_model,
                }
            ),
            200,
        )
    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/default-rag-config", methods=["PUT"])
def update_default_rag_config() -> tuple[Response, int]:
    """
    Create or update user's default RAG configuration.

    Headers:
        Authorization: Bearer <token>

    Request Body:
        {
            "embedding_model": "string",
            "embedding_dim": int | null,
            "retriever_type": "string",
            "chunk_size": int,
            "chunk_overlap": int,
            "top_k": int,
            "rerank_enabled": bool,
            "rerank_model": "string" | null
        }

    Returns:
        200: {
            "id": int,
            "user_id": int,
            "embedding_model": "string",
            "embedding_dim": int | null,
            "retriever_type": "string",
            "chunk_size": int,
            "chunk_overlap": int,
            "top_k": int,
            "rerank_enabled": bool,
            "rerank_model": "string" | null
        }
        400: {"error": "string"} - Invalid request
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Extract and validate fields
        embedding_model = data.get("embedding_model", "nomic-embed-text")
        embedding_dim = data.get("embedding_dim")
        retriever_type = data.get("retriever_type", "vector")
        chunk_size = data.get("chunk_size", 1000)
        chunk_overlap = data.get("chunk_overlap", 200)
        top_k = data.get("top_k", 8)
        rerank_enabled = data.get("rerank_enabled", False)
        rerank_model = data.get("rerank_model")

        # Validation
        if retriever_type not in ["vector", "graph", "hybrid"]:
            return jsonify({"error": "retriever_type must be 'vector', 'graph', or 'hybrid'"}), 400

        if not (100 <= chunk_size <= 5000):
            return jsonify({"error": "chunk_size must be between 100 and 5000"}), 400

        if not (0 <= chunk_overlap <= 1000):
            return jsonify({"error": "chunk_overlap must be between 0 and 1000"}), 400

        if not (1 <= top_k <= 50):
            return jsonify({"error": "top_k must be between 1 and 50"}), 400

        # Upsert configuration
        config = g.app_context.default_rag_config_repository.upsert(
            user_id=user.id,
            embedding_model=embedding_model,
            embedding_dim=embedding_dim,
            retriever_type=retriever_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
            rerank_enabled=rerank_enabled,
            rerank_model=rerank_model,
        )

        return (
            jsonify(
                {
                    "id": config.id,
                    "user_id": config.user_id,
                    "embedding_model": config.embedding_model,
                    "embedding_dim": config.embedding_dim,
                    "retriever_type": config.retriever_type,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_model": config.rerank_model,
                }
            ),
            200,
        )
    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401
