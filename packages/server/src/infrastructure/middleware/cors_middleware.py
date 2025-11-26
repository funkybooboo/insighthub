"""CORS middleware for cross-origin requests."""

from flask import Flask
from flask_cors import CORS

from src.infrastructure import config


def setup_cors_middleware(app: Flask) -> None:
    """
    Set up CORS middleware.

    Allows cross-origin requests from configured origins.

    Args:
        app: Flask application instance
    """
    CORS(
        app,
        origins=config.CORS_ORIGINS.split(",") if config.CORS_ORIGINS else ["*"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
