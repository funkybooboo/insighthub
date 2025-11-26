"""Mappers for converting between health domain models and DTOs."""

from typing import Any, Dict

from .dtos import (
    ConnectivityReport,
    HealthCheck,
    HealthStatus,
    LivenessStatus,
    MetricsData,
    ReadinessStatus,
    ServiceConnectivityCheck,
)


class HealthMapper:
    """Handles conversions between health domain models and DTOs."""

    @staticmethod
    def dict_to_health_status(data: Dict[str, Any]) -> HealthStatus:
        """
        Convert health status dictionary to HealthStatus DTO.

        Args:
            data: Health status dictionary

        Returns:
            HealthStatus DTO
        """
        checks = {}
        if "checks" in data and isinstance(data["checks"], dict):
            for name, check_data in data["checks"].items():
                if isinstance(check_data, dict):
                    checks[name] = HealthCheck(
                        status=check_data.get("status", "unknown"),
                        message=check_data.get("message", ""),
                        details=check_data.get("details"),
                        timestamp=check_data.get("timestamp"),
                    )

        return HealthStatus(
            status=data.get("status", "unknown"),
            timestamp=data.get("timestamp", ""),
            version=data.get("version", "unknown"),
            uptime=data.get("uptime"),
            checks=checks,
        )

    @staticmethod
    def health_status_to_dict(health_status: HealthStatus) -> Dict[str, any]:
        """
        Convert HealthStatus DTO to dictionary for JSON serialization.

        Args:
            health_status: HealthStatus DTO

        Returns:
            Dictionary representation
        """
        checks_dict = {}
        if health_status.checks:
            for name, check in health_status.checks.items():
                checks_dict[name] = {
                    "status": check.status,
                    "message": check.message,
                }
                if check.details:
                    checks_dict[name]["details"] = check.details
                if check.timestamp:
                    checks_dict[name]["timestamp"] = check.timestamp

        return {
            "status": health_status.status,
            "timestamp": health_status.timestamp,
            "version": health_status.version,
            "uptime": health_status.uptime,
            "checks": checks_dict,
        }

    @staticmethod
    def dict_to_readiness_status(data: Dict[str, any]) -> ReadinessStatus:
        """Convert readiness status dictionary to ReadinessStatus DTO."""
        return ReadinessStatus(status=data.get("status", "unknown"), message=data.get("message"))

    @staticmethod
    def readiness_status_to_dict(readiness: ReadinessStatus) -> Dict[str, any]:
        """Convert ReadinessStatus DTO to dictionary."""
        result = {"status": readiness.status}
        if readiness.message:
            result["message"] = readiness.message
        return result

    @staticmethod
    def dict_to_liveness_status(data: Dict[str, any]) -> LivenessStatus:
        """Convert liveness status dictionary to LivenessStatus DTO."""
        return LivenessStatus(status=data.get("status", "unknown"), message=data.get("message"))

    @staticmethod
    def liveness_status_to_dict(liveness: LivenessStatus) -> Dict[str, any]:
        """Convert LivenessStatus DTO to dictionary."""
        result = {"status": liveness.status}
        if liveness.message:
            result["message"] = liveness.message
        return result

    @staticmethod
    def dict_to_metrics_data(data: Dict[str, any]) -> MetricsData:
        """Convert metrics dictionary to MetricsData DTO."""
        return MetricsData(
            status=data.get("status", "unknown"),
            uptime=data.get("uptime"),
            memory_usage=data.get("memory_usage"),
            active_connections=data.get("active_connections", 0),
            total_requests=data.get("total_requests", 0),
            error_rate=data.get("error_rate", 0.0),
            avg_response_time=data.get("avg_response_time", 0.0),
            performance=data.get("performance"),
        )

    @staticmethod
    def metrics_data_to_dict(metrics: MetricsData) -> Dict[str, any]:
        """Convert MetricsData DTO to dictionary."""
        result = {
            "status": metrics.status,
            "active_connections": metrics.active_connections,
            "total_requests": metrics.total_requests,
            "error_rate": metrics.error_rate,
            "avg_response_time": metrics.avg_response_time,
        }

        if metrics.uptime:
            result["uptime"] = metrics.uptime
        if metrics.memory_usage:
            result["memory_usage"] = metrics.memory_usage
        if metrics.performance:
            result["performance"] = metrics.performance

        return result


class ConnectivityMapper:
    """Handles conversions for connectivity check DTOs."""

    @staticmethod
    def dict_to_connectivity_report(data: Dict[str, any]) -> ConnectivityReport:
        """
        Convert connectivity report dictionary to ConnectivityReport DTO.

        Args:
            data: Connectivity report dictionary

        Returns:
            ConnectivityReport DTO
        """
        services = []
        if "services" in data and isinstance(data["services"], list):
            for service_data in data["services"]:
                if isinstance(service_data, dict):
                    services.append(
                        ServiceConnectivityCheck(
                            service_name=service_data.get("service_name", "unknown"),
                            service_type=service_data.get("service_type", "unknown"),
                            is_connected=service_data.get("is_connected", False),
                            response_time_ms=service_data.get("response_time_ms"),
                            error_message=service_data.get("error_message"),
                            additional_info=service_data.get("additional_info"),
                        )
                    )

        return ConnectivityReport(
            timestamp=data.get("timestamp", ""),
            overall_status=data.get("overall_status", "unknown"),
            services=services,
        )

    @staticmethod
    def connectivity_report_to_dict(report: ConnectivityReport) -> Dict[str, any]:
        """
        Convert ConnectivityReport DTO to dictionary.

        Args:
            report: ConnectivityReport DTO

        Returns:
            Dictionary representation
        """
        services_list = []
        for service in report.services:
            service_dict = {
                "service_name": service.service_name,
                "service_type": service.service_type,
                "is_connected": service.is_connected,
            }
            if service.response_time_ms is not None:
                service_dict["response_time_ms"] = service.response_time_ms
            if service.error_message:
                service_dict["error_message"] = service.error_message
            if service.additional_info:
                service_dict["additional_info"] = service.additional_info
            services_list.append(service_dict)

        result = {
            "timestamp": report.timestamp,
            "overall_status": report.overall_status,
            "services": services_list,
        }

        if report.summary:
            result["summary"] = report.summary

        return result
