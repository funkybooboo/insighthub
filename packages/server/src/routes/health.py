"""Health check routes."""

from flask import Blueprint, Response, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/heartbeat", methods=["GET"])
def heartbeat() -> tuple[str, int]:
    """Simple heartbeat endpoint that returns 200 OK."""
    return "", 200


@health_bp.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """Health check endpoint with status information."""
    return jsonify({"status": "healthy"}), 200
