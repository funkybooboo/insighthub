"""Authentication routes."""

from flask import Blueprint, Response, g, jsonify, request
from jwt.exceptions import InvalidTokenError

from src.domains.auth.exceptions import UserAlreadyExistsError, UserAuthenticationError
from src.infrastructure.auth import create_access_token, get_current_user
from src.infrastructure.auth.decorators import require_auth
from src.infrastructure.logger import create_logger
from src.infrastructure.security import (
    InputSanitizer,
    get_client_ip,
    log_security_event,
    require_rate_limit,
)

logger = create_logger(__name__)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
@require_rate_limit(max_requests=3, window_seconds=3600)  # 3 signups per hour per IP
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
    # Get client IP for security logging
    client_ip = get_client_ip()

    data = request.get_json()
    if not data:
        log_security_event(
            "signup_failed", client_ip=client_ip, details={"reason": "no_request_body"}
        )
        return jsonify({"error": "Request body is required"}), 400

    # Sanitize and validate inputs
    username = InputSanitizer.sanitize_text(data.get("username", "")).lower()
    email = InputSanitizer.sanitize_text(data.get("email", "")).lower()
    password = data.get("password", "")
    full_name = InputSanitizer.sanitize_text(data.get("full_name", ""), max_length=100)

    # Comprehensive input validation
    if not username or not email or not password:
        log_security_event(
            "signup_failed",
            client_ip=client_ip,
            details={
                "reason": "missing_required_fields",
                "username": bool(username),
                "email": bool(email),
            },
        )
        return jsonify({"error": "username, email, and password are required"}), 400

    # Length checks to prevent DoS
    if len(username) > 50 or len(email) > 254 or len(password) > 128 or len(full_name) > 100:
        log_security_event(
            "signup_failed", client_ip=client_ip, details={"reason": "input_too_long"}
        )
        return jsonify({"error": "Input data too long"}), 400

    # Validate username format
    if not InputSanitizer.validate_username(username):
        log_security_event(
            "signup_failed",
            client_ip=client_ip,
            details={"reason": "invalid_username", "username": username[:20]},
        )
        return (
            jsonify(
                {
                    "error": "Username must be 3-50 characters and contain only letters, numbers, underscores, and hyphens"
                }
            ),
            400,
        )

    # Validate email format
    if not InputSanitizer.validate_email(email):
        log_security_event(
            "signup_failed",
            client_ip=client_ip,
            details={"reason": "invalid_email", "email": email[:30]},
        )
        return jsonify({"error": "Invalid email format"}), 400

    # Enhanced password validation
    password_validation = InputSanitizer.validate_password_strength(password)
    if not password_validation["valid"]:
        log_security_event(
            "signup_failed",
            client_ip=client_ip,
            details={"reason": "weak_password", "strength": password_validation["strength"]},
        )
        return (
            jsonify(
                {
                    "error": "Password does not meet security requirements",
                    "details": password_validation["errors"],
                    "strength": password_validation["strength"],
                    "requirements": [
                        "At least 8 characters long",
                        "Contains at least one uppercase letter",
                        "Contains at least one lowercase letter",
                        "Contains at least one number",
                        "Not a common password",
                    ],
                }
            ),
            400,
        )

    try:
        user = g.app_context.user_service.register_user(
            username=username, email=email, password=password, full_name=full_name
        )
        token = create_access_token(user.id)

        # Log successful registration
        log_security_event(
            "signup_successful",
            user_id=user.id,
            client_ip=client_ip,
            details={"username": username, "email": email[:30]},
        )

        response = jsonify(
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
        )

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response, 201

    except UserAlreadyExistsError as e:
        log_security_event(
            "signup_failed",
            client_ip=client_ip,
            details={"reason": "user_already_exists", "username": username, "email": email[:30]},
        )
        return jsonify({"error": str(e)}), 409  # Use 409 Conflict for existing user


@auth_bp.route("/login", methods=["POST"])
@require_rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
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
        429: {"error": "string"} - Rate limited
    """
    client_ip = get_client_ip()

    data = request.get_json()
    if not data:
        log_security_event(
            "login_failed", client_ip=client_ip, details={"reason": "no_request_body"}
        )
        return jsonify({"error": "Request body is required"}), 400

    username = InputSanitizer.sanitize_text(data.get("username", "")).lower()
    password = data.get("password", "")

    # Input validation
    if not username or not password:
        log_security_event(
            "login_failed",
            client_ip=client_ip,
            details={"reason": "missing_credentials", "username": bool(username)},
        )
        return jsonify({"error": "username and password are required"}), 400

    # Length checks
    if len(username) > 50 or len(password) > 128:
        log_security_event(
            "login_failed", client_ip=client_ip, details={"reason": "input_too_long"}
        )
        return jsonify({"error": "Input data too long"}), 400

    try:
        user = g.app_context.user_service.authenticate_user(username=username, password=password)
        token = create_access_token(user.id)

        # Log successful login
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
        log_security_event(
            event="login_failed",
            client_ip=request.remote_addr or "unknown",
            details={"username": username, "reason": str(e)},
        )
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/me", methods=["GET"])
@require_auth
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
        # Log successful profile access
        client_ip = get_client_ip()
        log_security_event("profile_accessed", user_id=user.id, client_ip=client_ip)
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
        client_ip = get_client_ip()
        log_security_event(
            "authentication_failed",
            client_ip=client_ip,
            details={"reason": "invalid_token", "error": str(e)},
        )
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/profile", methods=["PATCH"])
@require_rate_limit(max_requests=10, window_seconds=300)  # 10 updates per 5 minutes
@require_auth
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
    client_ip = get_client_ip()

    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            log_security_event(
                "profile_update_failed",
                user_id=user.id,
                client_ip=client_ip,
                details={"reason": "no_request_body"},
            )
            return jsonify({"error": "Request body is required"}), 400

        full_name = data.get("full_name")
        email = data.get("email")

        # Input validation and sanitization
        if full_name:
            full_name = InputSanitizer.sanitize_text(full_name, max_length=100)
            if len(full_name) > 100:
                log_security_event(
                    "profile_update_failed",
                    user_id=user.id,
                    client_ip=client_ip,
                    details={"reason": "full_name_too_long"},
                )
                return jsonify({"error": "Full name too long (max 100 characters)"}), 400

        if email:
            email = InputSanitizer.sanitize_text(email).lower()
            if not InputSanitizer.validate_email(email):
                log_security_event(
                    "profile_update_failed",
                    user_id=user.id,
                    client_ip=client_ip,
                    details={"reason": "invalid_email", "email": email[:30]},
                )
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


@auth_bp.route("/default-rag-config", methods=["GET"])
@require_auth
def get_default_rag_config() -> tuple[Response, int]:
    """
    Get the current user's default RAG configuration.

    Headers:
        Authorization: Bearer <token>

    Returns:
        200: VectorRagConfig | GraphRagConfig
        404: {"error": "No default RAG config found"}
        401: {"error": "Unauthorized"}
        500: {"error": "Server error"}
    """
    try:
        user = get_current_user()

        # Get default config from service
        config = g.app_context.default_rag_config_service.get_user_config(user.id)

        # Convert to the format expected by client (VectorRagConfig or GraphRagConfig)
        # For now, return vector config as default
        if config and config.vector_config:
            vector_config = config.vector_config
            response_data = {
                "embedding_algorithm": vector_config.get("embedding_algorithm", "nomic-embed-text"),
                "chunking_algorithm": vector_config.get("chunking_algorithm", "sentence"),
                "rerank_algorithm": vector_config.get("rerank_algorithm", "none"),
                "chunk_size": vector_config.get("chunk_size", 1000),
                "chunk_overlap": vector_config.get("chunk_overlap", 200),
                "top_k": vector_config.get("top_k", 8),
            }
            return jsonify(response_data), 200
        else:
            # Return default vector config if user has no saved config
            logger.info(f"Returning default RAG config for user {user.id} (no custom config found)")
            return (
                jsonify(
                    {
                        "embedding_algorithm": "nomic-embed-text",
                        "chunking_algorithm": "sentence",
                        "rerank_algorithm": "none",
                        "chunk_size": 1000,
                        "chunk_overlap": 200,
                        "top_k": 8,
                    }
                ),
                200,
            )

    except InvalidTokenError as e:
        logger.warning(f"Invalid token for default RAG config: {str(e)}")
        return jsonify({"error": "Invalid or expired token"}), 401
    except Exception as e:
        logger.error(f"Error getting default RAG config: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to get default RAG config: {str(e)}"}), 500


@auth_bp.route("/default-rag-config", methods=["PUT"])
@require_auth
def save_default_rag_config() -> tuple[Response, int]:
    """
    Save the current user's default RAG configuration.

    Request Body:
        VectorRagConfig | GraphRagConfig

    Returns:
        200: VectorRagConfig | GraphRagConfig
        400: {"error": "Invalid request"}
        500: {"error": "Server error"}
    """
    try:
        user = get_current_user()
        data = request.get_json() or {}

        # Convert from client format to server format
        vector_config = {
            "embedding_algorithm": data.get("embedding_algorithm", "nomic-embed-text"),
            "chunking_algorithm": data.get("chunking_algorithm", "sentence"),
            "rerank_algorithm": data.get("rerank_algorithm", "none"),
            "chunk_size": data.get("chunk_size", 1000),
            "chunk_overlap": data.get("chunk_overlap", 200),
            "top_k": data.get("top_k", 8),
        }

        g.app_context.default_rag_config_service.create_or_update_config(
            user_id=user.id,
            vector_config=vector_config,
            graph_config=None,  # Not supporting graph config in default for now
        )

        # Return in client format
        response_data = {
            "embedding_algorithm": vector_config["embedding_algorithm"],
            "chunking_algorithm": vector_config["chunking_algorithm"],
            "rerank_algorithm": vector_config["rerank_algorithm"],
            "chunk_size": vector_config["chunk_size"],
            "chunk_overlap": vector_config["chunk_overlap"],
            "top_k": vector_config["top_k"],
        }

        return jsonify(response_data), 200

    except InvalidTokenError as e:
        logger.warning(f"Invalid token for saving default RAG config: {str(e)}")
        return jsonify({"error": "Invalid or expired token"}), 401
    except Exception as e:
        logger.error(f"Error saving default RAG config: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to save default RAG config: {str(e)}"}), 500


@auth_bp.route("/preferences", methods=["PATCH"])
@require_auth
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


@auth_bp.route("/logout", methods=["POST"])
@require_rate_limit(max_requests=10, window_seconds=300)  # 10 logouts per 5 minutes
@require_auth
def logout() -> tuple[Response, int]:
    """
    Logout the current user.

    This endpoint primarily serves as a way to log the logout event.
    Client-side token removal should be handled by the client.

    Headers:
        Authorization: Bearer <token>

    Returns:
        200: {"message": "Logged out successfully"}
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        user = get_current_user()

        # Log logout event
        client_ip = get_client_ip()
        log_security_event("logout_successful", user_id=user.id, client_ip=client_ip)

        return jsonify({"message": "Logged out successfully"}), 200

    except InvalidTokenError as e:
        client_ip = get_client_ip()
        log_security_event(
            "logout_failed",
            client_ip=client_ip,
            details={"reason": "invalid_token", "error": str(e)},
        )
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/change-password", methods=["POST"])
@require_rate_limit(max_requests=3, window_seconds=3600)  # 3 password changes per hour
@require_auth
def change_password() -> tuple[Response, int]:
    """
    Change the current user's password.

    Headers:
        Authorization: Bearer <token>

    Request Body:
        {
            "current_password": "string",
            "new_password": "string"
        }

    Returns:
        200: {"message": "Password changed successfully"}
        400: {"error": "string"} - Invalid request or weak password
        401: {"error": "string"} - Invalid current password or token
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")

        if not current_password or not new_password:
            return jsonify({"error": "current_password and new_password are required"}), 400

        # Validate new password strength
        password_validation = InputSanitizer.validate_password_strength(new_password)
        if not password_validation["valid"]:
            return (
                jsonify(
                    {
                        "error": "New password does not meet security requirements",
                        "details": password_validation["errors"],
                        "strength": password_validation["strength"],
                        "requirements": [
                            "At least 8 characters long",
                            "Contains at least one uppercase letter",
                            "Contains at least one lowercase letter",
                            "Contains at least one number",
                            "Not a common password",
                        ],
                    }
                ),
                400,
            )

        # Change password via service
        success = g.app_context.user_service.change_password(
            user.id, current_password, new_password
        )

        if not success:
            return jsonify({"error": "Current password is incorrect"}), 401

        # Log password change
        client_ip = get_client_ip()
        log_security_event("password_changed", user_id=user.id, client_ip=client_ip)

        return jsonify({"message": "Password changed successfully"}), 200

    except InvalidTokenError as e:
        client_ip = get_client_ip()
        log_security_event(
            "password_change_failed",
            client_ip=client_ip,
            details={"reason": "invalid_token", "error": str(e)},
        )
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/users", methods=["GET"])
@require_auth
def list_users() -> tuple[Response, int]:
    """
    List all users with pagination.

    Query Parameters:
        skip: int - Number of users to skip (default: 0)
        limit: int - Maximum number of users to return (default: 100, max: 1000)

    Returns:
        200: {
            "users": [
                {
                    "id": int,
                    "username": "string",
                    "email": "string",
                    "full_name": "string",
                    "created_at": "string"
                }
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        400: {"error": "string"} - Invalid query parameters
        401: {"error": "string"} - Invalid or missing token
    """
    try:
        # Parse query parameters
        try:
            skip = int(request.args.get("skip", 0))
            limit = int(request.args.get("limit", 100))
        except ValueError:
            return jsonify({"error": "skip and limit must be integers"}), 400

        # Validate parameters
        if skip < 0:
            return jsonify({"error": "skip must be non-negative"}), 400
        if limit < 1 or limit > 1000:
            return jsonify({"error": "limit must be between 1 and 1000"}), 400

        # Get users from service
        users = g.app_context.user_service.list_users(skip=skip, limit=limit)

        # Get total count for pagination metadata
        total = g.app_context.user_service.count_users()

        return (
            jsonify(
                {
                    "users": [
                        {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "full_name": user.full_name,
                            "created_at": user.created_at.isoformat(),
                        }
                        for user in users
                    ],
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                }
            ),
            200,
        )

    except InvalidTokenError as e:
        return jsonify({"error": str(e)}), 401
