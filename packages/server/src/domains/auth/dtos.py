"""DTOs for authentication domain."""

from dataclasses import dataclass


@dataclass
class SignupRequest:
    """Request DTO for user signup."""

    username: str
    email: str
    password: str
    full_name: str | None = None


@dataclass
class LoginRequest:
    """Request DTO for user login."""

    username: str
    password: str


@dataclass
class AuthResponse:
    """Response DTO for authentication endpoints."""

    access_token: str
    token_type: str = "bearer"


@dataclass
class UserResponse:
    """Response DTO for user information."""

    id: int
    username: str
    email: str
    full_name: str | None
    created_at: str
    theme_preference: str = "dark"
