"""Authentication routes."""

from flask import Blueprint, Response, g, jsonify, request
from jwt.exceptions import InvalidTokenError
from src.domains.users.exceptions import UserAlreadyExistsError, UserAuthenticationError
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
