"""Health check routes."""

from flask import Blueprint, Response, current_app, jsonify

from src.infrastructure.database.sql_database import SqlDatabase
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/heartbeat", methods=["GET"])
def heartbeat() -> tuple[str, int]:
    """Simple heartbeat endpoint that returns 200 OK."""
    return "", 200


@health_bp.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """
    Comprehensive health check endpoint.

    Checks database connectivity, external services, and system components.
    Returns detailed health status for monitoring and debugging.
    """
    health_status: dict[str] = {
        "status": "healthy",
        "timestamp": "2025-11-24T00:00:00Z",  # Would be dynamic in real implementation
        "version": "1.0.0",
        "checks": {},
    }

    all_healthy = True

    # Database health check
    try:
        from src.infrastructure.database import get_db

        db: SqlDatabase = next(get_db())
        db.execute("SELECT 1")  # Simple query to test connectivity
        # Don't close singleton database connection
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection OK",
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}",
        }
        all_healthy = False

    # RAG system health check
    try:
        if hasattr(current_app, "rag_system") and current_app.rag_system:
            # Try a simple operation to test RAG system
            stats = current_app.rag_system.get_stats()
            health_status["checks"]["rag_system"] = {
                "status": "healthy",
                "message": "RAG system OK",
                "stats": stats,
            }
        else:
            health_status["checks"]["rag_system"] = {
                "status": "warning",
                "message": "RAG system not configured",
            }
    except Exception as e:
        health_status["checks"]["rag_system"] = {
            "status": "unhealthy",
            "message": f"RAG system error: {str(e)}",
        }
        all_healthy = False

    # External services health check
    try:
        from src.infrastructure.context import create_llm

        create_llm()
        # Test LLM connectivity with a simple validation
        health_status["checks"]["llm_service"] = {"status": "healthy", "message": "LLM service OK"}
    except Exception as e:
        health_status["checks"]["llm_service"] = {
            "status": "unhealthy",
            "message": f"LLM service error: {str(e)}",
        }
        all_healthy = False

    # Redis health check (if configured)
    try:
        import redis

        from src.infrastructure import config

        if config.REDIS_URL:
            redis_client = redis.from_url(config.REDIS_URL)
            redis_client.ping()
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "message": "Redis connection OK",
            }
        else:
            health_status["checks"]["redis"] = {
                "status": "warning",
                "message": "Redis not configured",
            }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis error: {str(e)}",
        }
        all_healthy = False

    # Update overall status
    health_status["status"] = "healthy" if all_healthy else "unhealthy"

    status_code = 200 if all_healthy else 503
    return jsonify(health_status), status_code


@health_bp.route("/ready", methods=["GET"])
def readiness() -> tuple[Response, int]:
    """
    Kubernetes readiness probe endpoint.

    Checks if the application is ready to serve traffic.
    Focuses on critical dependencies that must be available.
    """
    try:
        # Critical checks: database and basic app functionality
        from src.infrastructure.database import get_db

        db: SqlDatabase = next(get_db())
        db.execute("SELECT 1")
        # Don't close singleton database connection

        return jsonify({"status": "ready"}), 200
    except Exception:
        return jsonify({"status": "not ready"}), 503


@health_bp.route("/live", methods=["GET"])
def liveness() -> tuple[Response, int]:
    """
    Kubernetes liveness probe endpoint.

    Checks if the application is running and not in a broken state.
    """
    # Basic liveness check - if Flask is responding, we're alive
    return jsonify({"status": "alive"}), 200


@health_bp.route("/metrics", methods=["GET"])
def metrics() -> tuple[Response, int]:
    """
    Get application metrics and performance statistics.

    Returns:
    JSON response with metrics
    """
    metrics_data = {
        "status": "healthy",
        "uptime": "unknown",  # Would track actual uptime
        "memory_usage": "unknown",  # Would track memory stats
        "active_connections": 0,  # Would track WebSocket connections
    }

    # Add performance statistics if available
    if hasattr(current_app, "performance_monitoring"):
        perf_monitor = current_app.performance_monitoring
        metrics_data["performance"] = perf_monitor.get_stats()

    # Add request counts and error rates
    if hasattr(current_app, "performance_monitoring"):
        perf_monitor = current_app.performance_monitoring
        metrics_data.update(
            {
                "total_requests": perf_monitor.get_request_count(),
                "error_rate": perf_monitor.get_error_rate(),
                "avg_response_time": perf_monitor.get_avg_response_time(),
            }
        )

    return jsonify(metrics_data), 200


@health_bp.route("/docs", methods=["GET"])
def api_docs() -> tuple[Response, int]:
    """
    Get OpenAPI/Swagger documentation for the API.

    Returns basic API documentation with endpoint descriptions.
    """
    docs = {
        "openapi": "3.0.3",
        "info": {
            "title": "InsightHub API",
            "description": "RAG-powered document analysis and chats platform",
            "version": "1.0.0",
            "contact": {"name": "InsightHub Team"},
        },
        "servers": [{"url": "http://localhost:5000", "description": "Development server"}],
        "paths": {
            # Authentication endpoints
            "/api/auth/login": {
                "post": {
                    "summary": "User login",
                    "description": "Authenticate users with email/password",
                    "tags": ["Authentication"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email", "password"],
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 8},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "access_token": {"type": "string"},
                                            "token_type": {"type": "string"},
                                            "users": {"$ref": "#/components/schemas/User"},
                                        },
                                    }
                                }
                            },
                        },
                        "401": {"description": "Invalid credentials"},
                    },
                }
            },
            "/api/auth/signup": {
                "post": {
                    "summary": "User registration",
                    "description": "Create a new users account",
                    "tags": ["Authentication"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["username", "email", "password"],
                                    "properties": {
                                        "username": {"type": "string", "minLength": 3},
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 8},
                                        "full_name": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "User created successfully"},
                        "400": {"description": "Validation error"},
                        "409": {"description": "User already exists"},
                    },
                }
            },
            "/api/workspaces": {
                "get": {
                    "summary": "List workspaces",
                    "description": "Get all workspaces for the authenticated users",
                    "tags": ["Workspaces"],
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "List of workspaces",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Workspace"},
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create workspace",
                    "description": "Create a new workspace with RAG configuration",
                    "tags": ["Workspaces"],
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name"],
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 100,
                                        },
                                        "description": {"type": "string"},
                                        "rag_config": {"$ref": "#/components/schemas/RagConfig"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Workspace created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Workspace"}
                                }
                            },
                        }
                    },
                },
            },
            "/api/workspaces/{workspaceId}/chats/sessions/{sessionId}/messages": {
                "post": {
                    "summary": "Send chats message",
                    "description": "Send a message to a chats session and get AI response",
                    "tags": ["Chat"],
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "workspaceId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "name": "sessionId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["content"],
                                    "properties": {
                                        "content": {"type": "string", "maxLength": 10000},
                                        "message_type": {
                                            "type": "string",
                                            "enum": ["users", "system"],
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Message sent, response streamed via WebSocket"}
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "full_name": {"type": "string"},
                    },
                },
                "Workspace": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["provisioning", "ready", "deleting", "failed"],
                        },
                        "rag_config": {"$ref": "#/components/schemas/RagConfig"},
                        "document_count": {"type": "integer"},
                        "session_count": {"type": "integer"},
                    },
                },
                "RagConfig": {
                    "type": "object",
                    "properties": {
                        "embedding_model": {"type": "string"},
                        "retriever_type": {"type": "string", "enum": ["vector", "graph", "hybrid"]},
                        "chunk_size": {"type": "integer"},
                        "chunk_overlap": {"type": "integer"},
                        "top_k": {"type": "integer"},
                    },
                },
            },
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
        },
    }

    return jsonify(docs), 200
