"""Unit tests for JWT utilities."""

import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from jwt.exceptions import InvalidTokenError
from src.infrastructure.auth.jwt_utils import create_access_token, decode_access_token


class TestCreateAccessToken:
    """Tests for JWT token creation."""

    def test_create_access_token_returns_string(self) -> None:
        """Test that token creation returns a string."""
        token = create_access_token(user_id=1)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_user_id(self) -> None:
        """Test that token contains user_id in payload."""
        token = create_access_token(user_id=123)
        payload = decode_access_token(token)
        assert payload["user_id"] == 123

    def test_create_access_token_has_expiration(self) -> None:
        """Test that token has expiration time."""
        token = create_access_token(user_id=1)
        payload = decode_access_token(token)
        assert "exp" in payload
        assert payload["exp"] > time.time()

    def test_create_access_token_expiration_in_future(self) -> None:
        """Test that expiration is in the future."""
        with patch("src.infrastructure.auth.jwt_utils.ACCESS_TOKEN_EXPIRE_MINUTES", 60):
            token = create_access_token(user_id=1)
            payload = decode_access_token(token)

            now = datetime.utcnow()
            exp_time = datetime.utcfromtimestamp(payload["exp"])
            time_diff = (exp_time - now).total_seconds()

            assert time_diff > 3500
            assert time_diff < 3700

    def test_create_access_token_different_users(self) -> None:
        """Test that different users get different tokens."""
        token1 = create_access_token(user_id=1)
        token2 = create_access_token(user_id=2)

        assert token1 != token2

        payload1 = decode_access_token(token1)
        payload2 = decode_access_token(token2)

        assert payload1["user_id"] == 1
        assert payload2["user_id"] == 2


class TestDecodeAccessToken:
    """Tests for JWT token decoding."""

    def test_decode_access_token_success(self) -> None:
        """Test successfully decoding a valid token."""
        token = create_access_token(user_id=42)
        payload = decode_access_token(token)

        assert payload["user_id"] == 42
        assert "exp" in payload

    def test_decode_access_token_invalid_token(self) -> None:
        """Test decoding an invalid token."""
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            decode_access_token("invalid.token.here")

    def test_decode_access_token_malformed_token(self) -> None:
        """Test decoding a malformed token."""
        with pytest.raises(InvalidTokenError):
            decode_access_token("not-a-jwt-token")

    def test_decode_access_token_empty_token(self) -> None:
        """Test decoding an empty token."""
        with pytest.raises(InvalidTokenError):
            decode_access_token("")

    def test_decode_access_token_expired(self) -> None:
        """Test decoding an expired token."""
        with patch("src.infrastructure.auth.jwt_utils.ACCESS_TOKEN_EXPIRE_MINUTES", -1):
            token = create_access_token(user_id=1)

        time.sleep(0.1)

        with pytest.raises(InvalidTokenError, match="Token has expired"):
            decode_access_token(token)

    def test_decode_access_token_tampered(self) -> None:
        """Test decoding a tampered token."""
        token = create_access_token(user_id=1)
        tampered = token[:-10] + "tampered123"

        with pytest.raises(InvalidTokenError):
            decode_access_token(tampered)

    def test_decode_access_token_wrong_secret(self) -> None:
        """Test decoding token with wrong secret."""
        import jwt
        from src.infrastructure.auth.jwt_utils import ALGORITHM

        payload = {"user_id": 1, "exp": datetime.utcnow() + timedelta(minutes=60)}
        token = jwt.encode(payload, "wrong-secret-key", algorithm=ALGORITHM)

        with pytest.raises(InvalidTokenError):
            decode_access_token(token)


class TestTokenRoundtrip:
    """Tests for encoding and decoding tokens."""

    def test_token_roundtrip_preserves_data(self) -> None:
        """Test that encoding and decoding preserves user_id."""
        original_user_id = 999
        token = create_access_token(user_id=original_user_id)
        payload = decode_access_token(token)

        assert payload["user_id"] == original_user_id

    def test_multiple_tokens_independent(self) -> None:
        """Test that multiple tokens are independent."""
        tokens = [create_access_token(user_id=i) for i in range(5)]

        assert len(set(tokens)) == 5

        for i, token in enumerate(tokens):
            payload = decode_access_token(token)
            assert payload["user_id"] == i
