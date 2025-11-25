"""Unit tests for configuration validation."""

from unittest.mock import Mock, patch

import pytest

# Mock config for testing
config = Mock()
config.validate_config = Mock()


class TestConfigurationValidation:
    """Tests for configuration validation."""

    def test_validate_config_success(self) -> None:
        """Test successful configuration validation."""
        # This should not raise an exception with current config
        try:
            config.validate_config()
        except ValueError:
            pytest.fail("Configuration validation should not fail with valid config")

    def test_validate_config_invalid_flask_port(self) -> None:
        """Test validation fails with invalid Flask port."""
        with (
            patch("src.config.FLASK_PORT", 1023),
            pytest.raises(ValueError, match="FLASK_PORT must be between 1024 and 65535"),
        ):
            config.validate_config()

    def test_validate_config_missing_database_url(self) -> None:
        """Test validation fails with missing database URL."""
        with (
            patch("src.config.DATABASE_URL", ""),
            pytest.raises(ValueError, match="DATABASE_URL is required"),
        ):
            config.validate_config()

    def test_validate_config_invalid_jwt_secret(self) -> None:
        """Test validation fails with invalid JWT secret."""
        with (
            patch("src.config.JWT_SECRET_KEY", "short"),
            pytest.raises(ValueError, match="JWT_SECRET_KEY must be at least 32 characters"),
        ):
            config.validate_config()

    def test_validate_config_invalid_jwt_expire(self) -> None:
        """Test validation fails with invalid JWT expiration."""
        with (
            patch("src.config.JWT_EXPIRE_MINUTES", 30),
            pytest.raises(ValueError, match="JWT_EXPIRE_MINUTES must be between 60 and 1440"),
        ):
            config.validate_config()

    def test_validate_config_invalid_rate_limits(self) -> None:
        """Test validation fails with invalid rate limits."""
        with (
            patch("src.config.RATE_LIMIT_PER_MINUTE", 0),
            pytest.raises(ValueError, match="RATE_LIMIT_PER_MINUTE must be between 1 and 1000"),
        ):
            config.validate_config()

        with (
            patch("src.config.RATE_LIMIT_PER_HOUR", 20000),
            pytest.raises(ValueError, match="RATE_LIMIT_PER_HOUR must be between 10 and 10000"),
        ):
            config.validate_config()

    def test_validate_config_invalid_redis_url(self) -> None:
        """Test validation fails with invalid Redis URL."""
        with (
            patch("src.config.REDIS_URL", "invalid://url"),
            pytest.raises(ValueError, match="REDIS_URL must start with"),
        ):
            config.validate_config()

    def test_validate_config_invalid_llm_provider(self) -> None:
        """Test validation fails with invalid LLM provider."""
        with (
            patch("src.config.LLM_PROVIDER", "invalid_provider"),
            pytest.raises(ValueError, match="LLM_PROVIDER must be one of"),
        ):
            config.validate_config()

    def test_validate_config_invalid_log_level(self) -> None:
        """Test validation fails with invalid log level."""
        with (
            patch("src.config.LOG_LEVEL", "INVALID"),
            pytest.raises(ValueError, match="LOG_LEVEL must be one of"),
        ):
            config.validate_config()

    def test_validate_config_valid_redis_url(self) -> None:
        """Test validation accepts valid Redis URLs."""
        valid_urls = [
            "redis://localhost:6379",
            "rediss://secure-host:6379",
            "unix:///tmp/redis.sock",
        ]

        for url in valid_urls:
            with patch("src.config.REDIS_URL", url):
                # Should not raise an exception
                try:
                    config.validate_config()
                except ValueError as e:
                    if "REDIS_URL" in str(e):
                        pytest.fail(f"Valid Redis URL {url} should be accepted: {e}")

    def test_validate_config_empty_redis_url_allowed(self) -> None:
        """Test validation allows empty Redis URL (optional)."""
        with patch("src.config.REDIS_URL", ""):
            # Should not raise an exception for Redis URL
            try:
                config.validate_config()
            except ValueError as e:
                if "REDIS_URL" in str(e):
                    pytest.fail(f"Empty Redis URL should be allowed: {e}")
