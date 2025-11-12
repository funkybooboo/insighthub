"""Health check routes."""

from flask import Blueprint, Response, current_app, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/heartbeat", methods=["GET"])
def heartbeat() -> tuple[str, int]:
    """Simple heartbeat endpoint that returns 200 OK."""
    return "", 200


@health_bp.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """Health check endpoint with status information."""
    return jsonify({"status": "healthy"}), 200


@health_bp.route("/metrics", methods=["GET"])
def metrics() -> tuple[Response, int]:
    """
    Get application metrics and performance statistics.

    Returns:
        JSON response with metrics
    """
    metrics_data = {"status": "healthy"}

    # Add performance statistics if available
    if hasattr(current_app, "performance_monitoring"):
        perf_monitor = current_app.performance_monitoring
        metrics_data["performance"] = perf_monitor.get_stats()

    return jsonify(metrics_data), 200
