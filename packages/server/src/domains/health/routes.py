"""Health check routes for system monitoring."""

from flask import Blueprint, Response, g, jsonify

from .mappers import ConnectivityMapper, HealthMapper

health_bp = Blueprint("health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def get_health() -> tuple[Response, int]:
    """
    Get comprehensive health status of the system.

    Returns detailed health information including:
    - Overall system status
    - Individual service health checks
    - System uptime and version
    - Connectivity status for all dependencies

    Returns:
        200: {
            "status": "healthy" | "unhealthy" | "degraded",
            "timestamp": "ISO timestamp",
            "version": "string",
            "uptime": "string",
            "checks": {
                "service_name": {
                    "status": "healthy" | "unhealthy",
                    "message": "string",
                    "details": {...},
                    "timestamp": "ISO timestamp"
                }
            }
        }
        503: System is unhealthy
    """
    try:
        health_status = g.app_context.health_service.get_health_status()

        # Convert to response dict using mapper
        response_data = HealthMapper.health_status_to_dict(health_status)

        # Return appropriate HTTP status based on health
        if health_status.status == "healthy":
            status_code = 200
        elif health_status.status == "degraded":
            status_code = 200  # Still operational but with warnings
        else:  # unhealthy
            status_code = 503  # Service Unavailable

        return jsonify(response_data), status_code

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "timestamp": "unknown",
                    "version": "unknown",
                    "error": f"Health check failed: {str(e)}",
                }
            ),
            503,
        )


@health_bp.route("/readiness", methods=["GET"])
def get_readiness() -> tuple[Response, int]:
    """
    Readiness probe for Kubernetes.

    Checks if the application is ready to serve traffic by verifying
    critical dependencies (database, LLM service).

    Returns:
        200: {"status": "ready"}
        503: {"status": "not_ready", "message": "reason"}
    """
    try:
        readiness_status = g.app_context.health_service.get_readiness_status()

        # Convert to response dict using mapper
        response_data = HealthMapper.readiness_status_to_dict(readiness_status)

        status_code = 200 if readiness_status.status == "ready" else 503

        return jsonify(response_data), status_code

    except Exception as e:
        return jsonify({"status": "not_ready", "message": f"Readiness check failed: {str(e)}"}), 503


@health_bp.route("/liveness", methods=["GET"])
def get_liveness() -> tuple[Response, int]:
    """
    Liveness probe for Kubernetes.

    Basic check to determine if the application is running and responsive.
    If this fails, the pod should be restarted.

    Returns:
        200: {"status": "alive"}
    """
    try:
        liveness_status = g.app_context.health_service.get_liveness_status()

        # Convert to response dict using mapper
        response_data = HealthMapper.liveness_status_to_dict(liveness_status)

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"status": "dead", "message": f"Liveness check failed: {str(e)}"}), 503


@health_bp.route("/connectivity", methods=["GET"])
def get_connectivity() -> tuple[Response, int]:
    """
    Get detailed connectivity report for all system services.

    Tests connectivity to all external dependencies including:
    - Database (PostgreSQL)
    - Cache (Redis)
    - LLM Service (Ollama)
    - Vector Store (Qdrant)
    - Blob Storage
    - RAG System

    Returns:
        200: {
            "timestamp": "ISO timestamp",
            "overall_status": "all_connected" | "partial_failure" | "all_failed",
            "services": [
                {
                    "service_name": "string",
                    "service_type": "string",
                    "is_connected": boolean,
                    "response_time_ms": number,
                    "error_message": "string" | null,
                    "additional_info": {...} | null
                }
            ],
            "summary": {
                "connected": number,
                "failed": number,
                "total": number
            }
        }
    """
    try:
        connectivity_report = g.app_context.health_service.get_connectivity_report()

        # Convert to response dict using mapper
        response_data = ConnectivityMapper.connectivity_report_to_dict(connectivity_report)

        return jsonify(response_data), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "timestamp": "unknown",
                    "overall_status": "error",
                    "services": [],
                    "error": f"Connectivity check failed: {str(e)}",
                }
            ),
            503,
        )


@health_bp.route("/heartbeat", methods=["GET"])
def heartbeat() -> tuple[Response, int]:
    """
    Simple heartbeat endpoint for basic health checks.

    Returns a simple 200 response to indicate the application is running.
    Used by load balancers, monitoring systems, and basic health checks.

    Returns:
        200: {"status": "ok", "timestamp": "ISO timestamp"}
    """
    from datetime import datetime

    timestamp = datetime.now().isoformat() + "Z"

    return jsonify({"status": "ok", "timestamp": timestamp}), 200


@health_bp.route("/metrics", methods=["GET"])
def get_metrics() -> tuple[Response, int]:
    """
    Get application performance metrics.

    Returns basic metrics about system performance and usage.
    In production, this would be populated with real monitoring data.

    Returns:
        200: {
            "status": "string",
            "uptime": "string",
            "active_connections": number,
            "total_requests": number,
            "error_rate": number,
            "avg_response_time": number,
            "memory_usage": {...},
            "performance": {...}
        }
    """
    try:
        metrics_data = g.app_context.health_service.get_metrics()

        # Convert to response dict using mapper
        response_data = HealthMapper.metrics_data_to_dict(metrics_data)

        return jsonify(response_data), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "uptime": "unknown",
                    "active_connections": 0,
                    "total_requests": 0,
                    "error_rate": 0.0,
                    "avg_response_time": 0.0,
                    "error": f"Metrics retrieval failed: {str(e)}",
                }
            ),
            503,
        )
