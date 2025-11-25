"""Unit tests for logging configuration and functions."""

from unittest.mock import MagicMock, patch

from src.infrastructure.logging import (
    configure_logging,
    get_performance_logger,
    get_request_logger,
    get_security_logger,
    log_performance_metric,
    log_request_end,
    log_request_start,
    log_security_event,
)


class TestLoggingConfiguration:
    """Tests for logging configuration and utilities."""

    def test_configure_logging(self) -> None:
        """Test logging configuration setup."""
        with patch("src.infrastructure.logging.create_logger") as mock_create_logger:
            configure_logging()
            # Should create multiple loggers
            assert mock_create_logger.call_count > 0

    def test_get_request_logger(self) -> None:
        """Test getting request logger."""
        logger = get_request_logger()
        assert logger is not None
        assert hasattr(logger, "info")

    def test_get_security_logger(self) -> None:
        """Test getting security logger."""
        logger = get_security_logger()
        assert logger is not None
        assert hasattr(logger, "warning")

    def test_get_performance_logger(self) -> None:
        """Test getting performance logger."""
        logger = get_performance_logger()
        assert logger is not None
        assert hasattr(logger, "info")

    def test_log_request_start(self) -> None:
        """Test logging request start."""
        with patch("src.infrastructure.logging.get_request_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            log_request_start("GET", "/test", "127.0.0.1", 123, "corr-123")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "GET /test" in call_args[0][0]
            assert call_args[1]["extra"]["correlation_id"] == "corr-123"

    def test_log_request_end(self) -> None:
        """Test logging request end."""
        with patch("src.infrastructure.logging.get_request_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            log_request_end("GET", "/test", 200, 150.5, "corr-123")

            mock_logger.log.assert_called_once()
            call_args = mock_logger.log.call_args
            assert call_args[0][0] == 20  # INFO level
            assert "GET /test - 200" in call_args[0][1]
            assert call_args[1]["extra"]["correlation_id"] == "corr-123"
            assert call_args[1]["extra"]["response_time_ms"] == 150.5

    def test_log_request_end_error_status(self) -> None:
        """Test logging request end with error status."""
        with patch("src.infrastructure.logging.get_request_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            log_request_end("POST", "/api", 500, 200.0)

            mock_logger.log.assert_called_once()
            call_args = mock_logger.log.call_args
            assert call_args[0][0] == 40  # ERROR level

    def test_log_security_event(self) -> None:
        """Test logging security events."""
        with patch("src.infrastructure.logging.get_security_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            log_security_event(
                "login_failed", user_id=123, client_ip="192.168.1.1", details={"attempts": 3}
            )

            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args
            assert "login_failed" in call_args[0][0]
            assert call_args[1]["extra"]["user_id"] == 123
            assert call_args[1]["extra"]["client_ip"] == "192.168.1.1"
            assert call_args[1]["extra"]["details"]["attempts"] == 3

    def test_log_performance_metric(self) -> None:
        """Test logging performance metrics."""
        with patch("src.infrastructure.logging.get_performance_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            log_performance_metric("response_time", 150.5, {"endpoint": "/api/test"}, "corr-123")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "response_time = 150.5" in call_args[0][0]
            assert call_args[1]["extra"]["metric"] == "response_time"
            assert call_args[1]["extra"]["value"] == 150.5
            assert call_args[1]["extra"]["correlation_id"] == "corr-123"
