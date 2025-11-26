"""Health service for comprehensive system health monitoring."""

import time

from src.infrastructure.logger import create_logger

from .dtos import ConnectivityReport, HealthStatus, ReadinessStatus, LivenessStatus, MetricsData, \
    ServiceConnectivityCheck, HealthCheck

logger = create_logger(__name__)


class HealthService:
    """Service for comprehensive health monitoring and connectivity checks."""

    def __init__(self):
        """Initialize health service."""
        self.start_time = time.time()

    def get_uptime(self) -> str:
        """Get application uptime in human-readable format."""
        uptime_seconds = time.time() - self.start_time
        hours, remainder = divmod(int(uptime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def check_database_connectivity(self) -> ServiceConnectivityCheck:
        """Check database connectivity."""
        import time
        start_time = time.time()

        try:
            from src.infrastructure.database import get_db
            db = next(get_db())
            db.execute("SELECT 1")  # Simple connectivity test
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            logger.info(f"Database connectivity check successful: {response_time:.2f}ms")
            return ServiceConnectivityCheck(
                service_name="PostgreSQL Database",
                service_type="database",
                is_connected=True,
                response_time_ms=round(response_time, 2),
                additional_info={"query": "SELECT 1"}
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Database connectivity check failed: {str(e)} ({response_time:.2f}ms)")

            return ServiceConnectivityCheck(
                service_name="PostgreSQL Database",
                service_type="database",
                is_connected=False,
                response_time_ms=round(response_time, 2),
                error_message=str(e)
            )

    def check_redis_connectivity(self) -> ServiceConnectivityCheck:
        """Check Redis connectivity."""
        import time
        start_time = time.time()

        try:
            # Try to import and check Redis
            import redis

            # Check if Redis URL is configured
            try:
                from src import config
                redis_url = getattr(config, 'REDIS_URL', None)
            except (ImportError, AttributeError):
                redis_url = None

            if not redis_url:
                logger.warning("Redis connectivity check skipped: Redis not configured")
                return ServiceConnectivityCheck(
                    service_name="Redis Cache",
                    service_type="cache",
                    is_connected=False,
                    error_message="Redis not configured"
                )

            redis_client = redis.from_url(redis_url)
            redis_client.ping()
            response_time = (time.time() - start_time) * 1000

            logger.info(f"Redis connectivity check successful: {response_time:.2f}ms")
            return ServiceConnectivityCheck(
                service_name="Redis Cache",
                service_type="cache",
                is_connected=True,
                response_time_ms=round(response_time, 2),
                additional_info={"url": redis_url.replace(redis_url.split('@')[-1], '***')}  # Mask credentials
            )
        except ImportError:
            logger.warning("Redis connectivity check failed: Redis library not available")
            return ServiceConnectivityCheck(
                service_name="Redis Cache",
                service_type="cache",
                is_connected=False,
                error_message="Redis library not available"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Redis connectivity check failed: {str(e)} ({response_time:.2f}ms)")

            return ServiceConnectivityCheck(
                service_name="Redis Cache",
                service_type="cache",
                is_connected=False,
                response_time_ms=round(response_time, 2),
                error_message=str(e)
            )

    def check_llm_connectivity(self) -> ServiceConnectivityCheck:
        """Check LLM service connectivity."""
        import time
        start_time = time.time()

        try:
            # Try to create LLM provider (this tests connectivity)
            from src.context import create_llm
            llm_provider = create_llm()
            response_time = (time.time() - start_time) * 1000

            logger.info(f"LLM connectivity check successful: {response_time:.2f}ms")
            return ServiceConnectivityCheck(
                service_name="LLM Service (Ollama)",
                service_type="external_api",
                is_connected=True,
                response_time_ms=round(response_time, 2),
                additional_info={"provider_type": "ollama"}
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"LLM connectivity check failed: {str(e)} ({response_time:.2f}ms)")

            return ServiceConnectivityCheck(
                service_name="LLM Service (Ollama)",
                service_type="external_api",
                is_connected=False,
                response_time_ms=round(response_time, 2),
                error_message=str(e)
            )

    def check_vector_store_connectivity(self) -> ServiceConnectivityCheck:
        """Check vector store connectivity."""
        import time
        start_time = time.time()

        try:
            # Try to create vector store and do a simple operation
            from src.infrastructure.rag.steps.vector_rag.vector_stores import create_vector_store

            # Use default configuration for health check
            vector_store = create_vector_store(
                db_type="qdrant",
                url="http://localhost:6333",
                collection_name="health_check",
                vector_size=384
            )

            if vector_store:
                # Try a simple search (should work even with empty collection)
                results = vector_store.search([0.1] * 384, top_k=1)
                response_time = (time.time() - start_time) * 1000

                logger.info(f"Vector store connectivity check successful: {response_time:.2f}ms")
                return ServiceConnectivityCheck(
                    service_name="Qdrant Vector Store",
                    service_type="storage",
                    is_connected=True,
                    response_time_ms=round(response_time, 2),
                    additional_info={"collection": "health_check", "vector_size": 384}
                )
            else:
                logger.error("Vector store connectivity check failed: Vector store creation failed")
                return ServiceConnectivityCheck(
                    service_name="Qdrant Vector Store",
                    service_type="storage",
                    is_connected=False,
                    error_message="Vector store creation failed"
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Vector store connectivity check failed: {str(e)} ({response_time:.2f}ms)")

            return ServiceConnectivityCheck(
                service_name="Qdrant Vector Store",
                service_type="storage",
                is_connected=False,
                response_time_ms=round(response_time, 2),
                error_message=str(e)
            )

    def check_blob_storage_connectivity(self) -> ServiceConnectivityCheck:
        """Check blob storage connectivity."""
        import time
        start_time = time.time()

        try:
            from src.infrastructure.storage import create_blob_storage

            blob_storage = create_blob_storage()
            # Try to list objects (should work even if empty)
            objects = blob_storage.list("")
            response_time = (time.time() - start_time) * 1000

            logger.info(f"Blob storage connectivity check successful: {response_time:.2f}ms")
            return ServiceConnectivityCheck(
                service_name="Blob Storage",
                service_type="storage",
                is_connected=True,
                response_time_ms=round(response_time, 2),
                additional_info={"object_count": len(objects) if hasattr(objects, '__len__') else 'unknown'}
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Blob storage connectivity check failed: {str(e)} ({response_time:.2f}ms)")

            return ServiceConnectivityCheck(
                service_name="Blob Storage",
                service_type="storage",
                is_connected=False,
                response_time_ms=round(response_time, 2),
                error_message=str(e)
            )

    def check_rag_system_connectivity(self) -> ServiceConnectivityCheck:
        """Check RAG system connectivity."""
        import time
        start_time = time.time()

        try:
            from flask import current_app

            if hasattr(current_app, "rag_system") and current_app.rag_system:
                # Try to get stats from RAG system
                stats = current_app.rag_system.get_stats()
                response_time = (time.time() - start_time) * 1000

                logger.info(f"RAG system connectivity check successful: {response_time:.2f}ms")
                return ServiceConnectivityCheck(
                    service_name="RAG System",
                    service_type="application",
                    is_connected=True,
                    response_time_ms=round(response_time, 2),
                    additional_info=stats if isinstance(stats, dict) else {"status": "operational"}
                )
            else:
                logger.warning("RAG system connectivity check failed: RAG system not configured")
                return ServiceConnectivityCheck(
                    service_name="RAG System",
                    service_type="application",
                    is_connected=False,
                    error_message="RAG system not configured"
                )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"RAG system connectivity check failed: {str(e)} ({response_time:.2f}ms)")

            return ServiceConnectivityCheck(
                service_name="RAG System",
                service_type="application",
                is_connected=False,
                response_time_ms=round(response_time, 2),
                error_message=str(e)
            )

    def get_connectivity_report(self) -> ConnectivityReport:
        """Get comprehensive connectivity report for all services."""
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        logger.info("Starting comprehensive connectivity report")
        services = [
            self.check_database_connectivity(),
            self.check_redis_connectivity(),
            self.check_llm_connectivity(),
            self.check_vector_store_connectivity(),
            self.check_blob_storage_connectivity(),
            self.check_rag_system_connectivity(),
        ]

        # Determine overall status
        connected_count = sum(1 for s in services if s.is_connected)
        if connected_count == len(services):
            overall_status = "all_connected"
            logger.info(f"Connectivity report completed: {connected_count}/{len(services)} services connected")
        elif connected_count == 0:
            overall_status = "all_failed"
            logger.error(f"Connectivity report completed: {connected_count}/{len(services)} services connected - all services failed")
        else:
            overall_status = "partial_failure"
            logger.warning(f"Connectivity report completed: {connected_count}/{len(services)} services connected - partial failure")

        return ConnectivityReport(
            timestamp=timestamp,
            overall_status=overall_status,
            services=services
        )

    def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status."""
        import time
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Run connectivity checks
        connectivity_report = self.get_connectivity_report()

        # Determine overall health
        critical_services = ["PostgreSQL Database", "LLM Service (Ollama)"]
        critical_failures = [
            s for s in connectivity_report.services
            if s.service_name in critical_services and not s.is_connected
        ]

        if critical_failures:
            overall_status = "unhealthy"
        elif connectivity_report.overall_status == "partial_failure":
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        # Convert connectivity checks to health checks
        checks = {}
        for service in connectivity_report.services:
            status = "healthy" if service.is_connected else "unhealthy"
            message = f"Connected ({service.response_time_ms:.1f}ms)" if service.is_connected else f"Failed: {service.error_message}"

            checks[service.service_name.lower().replace(" ", "_")] = HealthCheck(
                status=status,
                message=message,
                details={
                    "service_type": service.service_type,
                    "response_time_ms": service.response_time_ms,
                    "additional_info": service.additional_info
                } if service.additional_info else None,
                timestamp=timestamp
            )

        return HealthStatus(
            status=overall_status,
            timestamp=timestamp,
            version="1.0.0",
            uptime=self.get_uptime(),
            checks=checks
        )

    def get_readiness_status(self) -> ReadinessStatus:
        """Get readiness status for Kubernetes."""
        # Check critical dependencies
        db_check = self.check_database_connectivity()
        llm_check = self.check_llm_connectivity()

        if db_check.is_connected and llm_check.is_connected:
            return ReadinessStatus(status="ready")
        else:
            failed_services = []
            if not db_check.is_connected:
                failed_services.append("database")
            if not llm_check.is_connected:
                failed_services.append("llm")

            return ReadinessStatus(
                status="not_ready",
                message=f"Critical services unavailable: {', '.join(failed_services)}"
            )

    def get_liveness_status(self) -> LivenessStatus:
        """Get liveness status for Kubernetes."""
        # Basic liveness check - if we can execute this, we're alive
        return LivenessStatus(status="alive")

    def get_metrics(self) -> MetricsData:
        """Get application metrics."""
        # Basic metrics - in a real app, this would collect from monitoring systems
        return MetricsData(
            status="healthy",
            uptime=self.get_uptime(),
            active_connections=0,  # Would be populated from WebSocket monitoring
            total_requests=0,      # Would be populated from request monitoring
            error_rate=0.0,        # Would be calculated from error monitoring
            avg_response_time=0.0  # Would be calculated from response time monitoring
        )
