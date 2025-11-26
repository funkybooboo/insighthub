"""DTOs for health domain."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class HealthCheck:
    """DTO for individual health check result."""

    status: str  # "healthy", "unhealthy", "warning"
    message: str
    details: Dict[str, Any] | None = None
    timestamp: str | None = None


@dataclass
class HealthStatus:
    """DTO for overall health status."""

    status: str  # "healthy", "unhealthy", "degraded"
    timestamp: str
    version: str
    uptime: str | None = None
    checks: Dict[str, HealthCheck] | None = None

    def __post_init__(self):
        if self.checks is None:
            self.checks = {}


@dataclass
class ReadinessStatus:
    """DTO for readiness probe status."""

    status: str  # "ready", "not_ready"
    message: str | None = None


@dataclass
class LivenessStatus:
    """DTO for liveness probe status."""

    status: str  # "alive", "dead"
    message: str | None = None


@dataclass
class MetricsData:
    """DTO for application metrics."""

    status: str
    uptime: str | None = None
    memory_usage: Dict[str, Any] | None = None
    active_connections: int = 0
    total_requests: int = 0
    error_rate: float = 0.0
    avg_response_time: float = 0.0
    performance: Dict[str, Any] | None = None


@dataclass
class ServiceConnectivityCheck:
    """DTO for service connectivity check result."""

    service_name: str
    service_type: str  # "database", "cache", "queue", "storage", "external_api", etc.
    is_connected: bool
    response_time_ms: float | None = None
    error_message: str | None = None
    additional_info: Dict[str, Any] | None = None


@dataclass
class ConnectivityReport:
    """DTO for comprehensive connectivity report."""

    timestamp: str
    overall_status: str  # "all_connected", "partial_failure", "all_failed"
    services: list[ServiceConnectivityCheck]
    summary: Dict[str, int] | None = None  # connected, failed, total

    def __post_init__(self):
        if self.summary is None:
            connected = sum(1 for s in self.services if s.is_connected)
            failed = len(self.services) - connected
            self.summary = {
                "connected": connected,
                "failed": failed,
                "total": len(self.services)
            }
