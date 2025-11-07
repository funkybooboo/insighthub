"""API routes package."""

from .chat_route import chat_bp
from .document_route import documents_bp
from .health_route import health_bp

__all__ = ["health_bp", "documents_bp", "chat_bp"]
