"""Authentication routes."""

from flask import Blueprint, Response, g, jsonify, request
from jwt.exceptions import InvalidTokenError

from src.infrastructure.auth import create_access_token, get_current_user
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup() -> tuple[Response, int]:
    """
    Register a new users.

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
            "users": {
                "id": int,
                "username": "string",
                "email": "string",
                "full_name": "string",
                "created_at": "string"
            }
        }
        400: {"error": "string"} - Validation error or users already exists
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    from src.infrastructure.security.input_sanitizer import InputSanitizer

    username = InputSanitizer.sanitize_text(data.get("username", ""))
    email = InputSanitizer.sanitize_text(data.get("email", ""))
    password = data.get("password", "")  # Don't sanitize password
    full_name = InputSanitizer.sanitize_text(data.get("full_name", ""), max_length=100)

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    # Validate input formats
    if not InputSanitizer.validate_username(username):
        return (
            jsonify(
                {
                    "error": "Username must be 3-50 characters and contain only letters, numbers, underscores, and hyphens"
                }
            ),
            400,
        )

    if not InputSanitizer.validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Enhanced password validation
    password_validation = InputSanitizer.validate_password_strength(password)
    if not password_validation["valid"]:
        return (
            jsonify(
                {
                    "error": "Password does not meet requirements",
                    "details": password_validation["errors"],
                    "strength": password_validation["strength"],
                }
            ),
            400,
        )

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
                    "users": {
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
@require_rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
def login() -> tuple[Response, int]:
    """
    Authenticate a users and return a JWT token.

    Request Body:
        {
            "username": "string",
            "password": "string"
        }

    Returns:
        200: {
            "access_token": "string",
            "token_type": "bearer",
            "users": {
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

        # Log successful login
        from flask import request

        from src.infrastructure.logging import log_security_event

        log_security_event(
            event="login_successful", user_id=user.id, client_ip=request.remote_addr or "unknown"
        )

        return (
            jsonify(
                {
                    "access_token": token,
                    "token_type": "bearer",
                    "users": {
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
        # Log failed login attempt
        from flask import request

        from src.infrastructure.logging import log_security_event

        log_security_event(
            event="login_failed",
            client_ip=request.remote_addr or "unknown",
            details={"username": username, "reason": str(e)},
        )
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/me", methods=["GET"])
def get_me() -> tuple[Response, int]:
    """
    Get the current authenticated users's information.

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
    Change users password.

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

        # Comprehensive password validation
        if len(new_password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400

        if not any(c.isupper() for c in new_password):
            return jsonify({"error": "Password must contain at least one uppercase letter"}), 400

        if not any(c.islower() for c in new_password):
            return jsonify({"error": "Password must contain at least one lowercase letter"}), 400

        if not any(c.isdigit() for c in new_password):
            return jsonify({"error": "Password must contain at least one number"}), 400

        # Check for common weak passwords
        weak_passwords = ["password", "123456", "qwerty", "abc123", "password123"]
        if new_password.lower() in weak_passwords:
            return (
                jsonify({"error": "Password is too common, please choose a stronger password"}),
                400,
            )

        # Verify current password
        if not user.check_password(current_password):
            # Log failed password verification
            from flask import request

            from src.infrastructure.logging import log_security_event

            log_security_event(
                event="password_change_failed",
                user_id=user.id,
                client_ip=request.remote_addr or "unknown",
                details={"reason": "incorrect_current_password"},
            )
            return jsonify({"error": "Current password is incorrect"}), 401

        # Update password
        user.set_password(new_password)
        g.app_context.user_service.update_user(user.id)

        # Log successful password change
        from flask import request

        from src.infrastructure.logging import log_security_event

        log_security_event(
            event="password_changed", user_id=user.id, client_ip=request.remote_addr or "unknown"
        )

        return jsonify({"message": "Password changed successfully"}), 200

    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/profile", methods=["PATCH"])
def update_profile() -> tuple[Response, int]:
    """
    Update users profile.

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

        # Update users
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
    Update users preferences.

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
    Get users's default RAG configuration.

    Headers:
        Authorization: Bearer <token>

    Returns:
        200: {
            "id": int,
            "user_id": int,
            "vector_config": {
                "embedding_algorithm": "string",
                "chunking_algorithm": "string",
                "rerank_algorithm": "string",
                "chunk_size": int,
                "chunk_overlap": int,
                "top_k": int
            },
            "graph_config": {
                "entity_extraction_algorithm": "string",
                "relationship_extraction_algorithm": "string",
                "clustering_algorithm": "string"
            }
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
                    "vector_config": {
                        "embedding_algorithm": config.vector_config.embedding_algorithm,
                        "chunking_algorithm": config.vector_config.chunking_algorithm,
                        "rerank_algorithm": config.vector_config.rerank_algorithm,
                        "chunk_size": config.vector_config.chunk_size,
                        "chunk_overlap": config.vector_config.chunk_overlap,
                        "top_k": config.vector_config.top_k,
                    },
                    "graph_config": {
                        "entity_extraction_algorithm": config.graph_config.entity_extraction_algorithm,
                        "relationship_extraction_algorithm": config.graph_config.relationship_extraction_algorithm,
                        "clustering_algorithm": config.graph_config.clustering_algorithm,
                    },
                }
            ),
            200,
        )
    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/default-rag-config", methods=["PUT"])
def update_default_rag_config() -> tuple[Response, int]:
    """
    Create or update users's default RAG configuration.

    Headers:
        Authorization: Bearer <token>

    Request Body:
        {
            "vector_config": {
                "embedding_algorithm": "string",
                "chunking_algorithm": "string",
                "rerank_algorithm": "string",
                "chunk_size": int,
                "chunk_overlap": int,
                "top_k": int
            },
            "graph_config": {
                "entity_extraction_algorithm": "string",
                "relationship_extraction_algorithm": "string",
                "clustering_algorithm": "string"
            }
        }

    Returns:
        200: {
            "id": int,
            "user_id": int,
            "vector_config": {...},
            "graph_config": {...}
        }
        400: {"error": "string"} - Invalid request
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Use the service instead of calling repository directly
        config = g.app_context.default_rag_config_service.create_or_update_config(
            user_id=user.id,
            vector_config=data.get("vector_config"),
            graph_config=data.get("graph_config"),
        )

        return (
            jsonify(
                {
                    "id": config.id,
                    "user_id": config.user_id,
                    "vector_config": {
                        "embedding_algorithm": config.vector_config.embedding_algorithm,
                        "chunking_algorithm": config.vector_config.chunking_algorithm,
                        "rerank_algorithm": config.vector_config.rerank_algorithm,
                        "chunk_size": config.vector_config.chunk_size,
                        "chunk_overlap": config.vector_config.chunk_overlap,
                        "top_k": config.vector_config.top_k,
                    },
                    "graph_config": {
                        "entity_extraction_algorithm": config.graph_config.entity_extraction_algorithm,
                        "relationship_extraction_algorithm": config.graph_config.relationship_extraction_algorithm,
                        "clustering_algorithm": config.graph_config.clustering_algorithm,
                    },
                }
            ),
            200,
        )
    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401
