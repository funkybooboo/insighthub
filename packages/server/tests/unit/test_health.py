"""Unit tests for health domain."""

import time
import pytest

from src.domains.health.service import HealthService


@pytest.mark.unit
class TestHealthService:
    """Test cases for HealthService."""

    def test_get_uptime_returns_string(self):
        """Test that get_uptime returns a string."""
        service = HealthService()
        uptime = service.get_uptime()

        assert isinstance(uptime, str)
        assert len(uptime) > 0

    def test_get_uptime_format_seconds(self):
        """Test uptime format when less than 1 minute."""
        service = HealthService()
        # Mock start_time to be 45 seconds ago
        service.start_time = time.time() - 45

        uptime = service.get_uptime()
        assert "45s" in uptime

    def test_get_uptime_format_minutes(self):
        """Test uptime format when less than 1 hour."""
        service = HealthService()
        # Mock start_time to be 5 minutes and 30 seconds ago
        service.start_time = time.time() - (5 * 60 + 30)

        uptime = service.get_uptime()
        assert "5m 30s" in uptime

    def test_get_uptime_format_hours(self):
        """Test uptime format when more than 1 hour."""
        service = HealthService()
        # Mock start_time to be 2 hours, 15 minutes and 45 seconds ago
        service.start_time = time.time() - (2 * 3600 + 15 * 60 + 45)

        uptime = service.get_uptime()
        assert "2h 15m 45s" in uptime