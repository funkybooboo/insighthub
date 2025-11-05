"""
SQLAlchemy models for users, documents, and chat history.

DEPRECATED: This module is kept for backward compatibility.
Please import from db.models instead.
"""

from .models import ChatMessage, ChatSession, Document, User

__all__ = ["User", "Document", "ChatSession", "ChatMessage"]
