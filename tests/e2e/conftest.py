"""Pytest configuration for E2E tests.

This module ensures backing services (PostgreSQL, Ollama, Qdrant, Neo4j, MinIO, Redis)
are running before E2E tests execute. If services are not running, it attempts to start
them once using docker compose. If they still don't start, tests fail with a clear message.
"""

import subprocess
import time
from typing import Literal

import pytest


def check_service_health(service: str) -> Literal["healthy", "unhealthy", "not_running"]:
    """Check if a Docker Compose service is healthy.

    Args:
        service: Name of the service to check

    Returns:
        "healthy" if service is running and healthy
        "unhealthy" if service is running but not healthy
        "not_running" if service is not running
    """
    try:
        # Check if service is running
        state_result = subprocess.run(
            ["docker", "compose", "ps", service, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )

        if not state_result.stdout.strip():
            return "not_running"

        # Parse state and health from JSON output
        import json

        service_info = json.loads(state_result.stdout)

        state = service_info.get("State", "unknown")
        health = service_info.get("Health", "unknown")

        if state != "running":
            return "not_running"

        # If service doesn't have a healthcheck, assume healthy if running
        if health in ("healthy", "unknown"):
            return "healthy"

        return "unhealthy"

    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        return "not_running"


def check_all_services_healthy() -> tuple[bool, list[str]]:
    """Check if all backing services are healthy.

    Returns:
        Tuple of (all_healthy, list of unhealthy service names)
    """
    services = ["postgres", "ollama", "qdrant", "neo4j", "minio", "redis"]
    unhealthy_services = []

    for service in services:
        status = check_service_health(service)
        if status != "healthy":
            unhealthy_services.append(f"{service} ({status})")

    return len(unhealthy_services) == 0, unhealthy_services


def start_services() -> bool:
    """Start backing services using docker compose.

    Returns:
        True if services started successfully, False otherwise
    """
    try:
        print("\n[WARNING] Backing services not running. Attempting to start them...")
        subprocess.run(
            ["docker", "compose", "up", "-d"],
            check=True,
            capture_output=True,
        )

        # Wait for services to become healthy (max 60 seconds)
        print("[INFO] Waiting for services to become healthy...")
        max_wait = 60
        wait_interval = 2
        elapsed = 0

        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval

            all_healthy, unhealthy = check_all_services_healthy()
            if all_healthy:
                print(f"[OK] All services are healthy after {elapsed}s")
                return True

            print(f"   Waiting... ({elapsed}s) - Unhealthy: {', '.join(unhealthy)}")

        print(f"[FAIL] Services did not become healthy after {max_wait}s")
        return False

    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Failed to start services: {e}")
        return False


@pytest.fixture(scope="session", autouse=True)
def ensure_backing_services():
    """Ensure backing services are running before E2E tests.

    This fixture runs once per test session and:
    1. Checks if all backing services are healthy
    2. If not, attempts to start them once
    3. Checks again after starting
    4. Fails the test session if services still aren't healthy
    """
    all_healthy, unhealthy = check_all_services_healthy()

    if all_healthy:
        print("\n[OK] All backing services are healthy")
        return

    # Services not healthy - try to start them once
    print(f"\n[WARNING] Some services are not healthy: {', '.join(unhealthy)}")
    started = start_services()

    if not started:
        pytest.exit(
            "[FAIL] Failed to start backing services. Please run 'task up' manually "
            "and ensure all services are healthy before running E2E tests.",
            returncode=1,
        )

    # Verify services are now healthy
    all_healthy, still_unhealthy = check_all_services_healthy()

    if not all_healthy:
        pytest.exit(
            f"[FAIL] Backing services started but some are still unhealthy: {', '.join(still_unhealthy)}. "
            "Please check service logs with 'task logs' and ensure all services are healthy.",
            returncode=1,
        )

    print("[OK] All backing services are now healthy and ready for E2E tests")
