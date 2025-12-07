"""Chat session data access layer - coordinates cache and repository."""

import json
from datetime import UTC, datetime
from typing import Optional

from returns.result import Result

from src.cache_keys import CacheKeys
from src.domains.workspace.chat.session.models import ChatSession
from src.domains.workspace.chat.session.repositories import ChatSessionRepository
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger
from src.infrastructure.types import DatabaseError, Pagination, PaginatedResult

logger = create_logger(__name__)


class ChatSessionDataAccess:
    """Data access layer for ChatSession - handles caching + persistence."""

    def __init__(self, repository: ChatSessionRepository, cache: Optional[Cache] = None):
        """Initialize data access layer.

        Args:
            repository: ChatSession repository for database operations
            cache: Optional cache for performance optimization
        """
        self.repository = repository  # Exposed for operations not handled by this layer
        self.cache = cache

    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID with caching.

        Args:
            session_id: Chat session ID

        Returns:
            ChatSession if found, None otherwise
        """
        # Try cache first
        cache_key = CacheKeys.chat_session(session_id)
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
                return ChatSession(
                    id=data["id"],
                    workspace_id=data.get("workspace_id"),
                    title=data.get("title"),
                    rag_type=data["rag_type"],
                    created_at=(
                        datetime.fromisoformat(data["created_at"])
                        if data.get("created_at")
                        else datetime.now(UTC)
                    ),
                    updated_at=(
                        datetime.fromisoformat(data["updated_at"])
                        if data.get("updated_at")
                        else datetime.now(UTC)
                    ),
                )
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                logger.warning(f"Cache deserialization error for chat session {session_id}: {e}")

        # Cache miss - fetch from database
        session = self.repository.get_by_id(session_id)

        if session and self.cache:
            self._cache_session(session)

        return session

    def get_all(self, pagination: Pagination) -> PaginatedResult[ChatSession]:
        """Get all chat sessions with caching.

        Args:
            pagination: Pagination parameters

        Returns:
            PaginatedResult of chat sessions
        """
        # For paginated queries, we don't cache the list itself
        # but we cache individual sessions that are fetched
        result = self.repository.get_all(pagination)

        if self.cache:
            for session in result.items:
                self._cache_session(session)

        return result

    def get_by_workspace(
        self, workspace_id: int, pagination: Pagination
    ) -> PaginatedResult[ChatSession]:
        """Get sessions by workspace with caching.

        Args:
            workspace_id: Workspace ID
            pagination: Pagination parameters

        Returns:
            PaginatedResult of chat sessions
        """
        # Try cache first for cache-eligible queries (first page, reasonable size)
        if pagination.is_cache_eligible():
            cache_key = CacheKeys.workspace_chat_sessions(workspace_id)
            cached_json = self.cache.get(cache_key) if self.cache else None

            if cached_json:
                cached_result = self._try_get_cached_sessions(cache_key, cached_json, pagination)
                if cached_result is not None:
                    return cached_result

        # Cache miss or pagination - fetch from database
        result = self.repository.get_by_workspace(workspace_id, pagination)

        # Cache the result for first page
        if self.cache and pagination.is_cache_eligible() and result.items:
            cache_value = json.dumps([s.id for s in result.items])
            self.cache.set(
                CacheKeys.workspace_chat_sessions(workspace_id), cache_value, ttl=120
            )  # Cache for 2 minutes
            # Also cache individual sessions
            for session in result.items:
                self._cache_session(session)

        return result

    def _try_get_cached_sessions(
        self, cache_key: str, cached_json: str, pagination: Pagination
    ) -> Optional[PaginatedResult[ChatSession]]:
        """Try to retrieve sessions from cache.

        Returns:
            PaginatedResult if all found, None if any missing or invalid
        """
        try:
            session_ids = json.loads(cached_json)
            sessions = []
            skip, limit = pagination.offset_limit()
            for sess_id in session_ids[:limit]:
                sess = self.get_by_id(sess_id)
                if not sess:
                    if self.cache:
                        self.cache.delete(cache_key)
                    return None
                sessions.append(sess)
            # Note: For cached results, we use the length as total_count
            # This is a simplification since we only cache first page
            return PaginatedResult(
                items=sessions, total_count=len(session_ids), skip=skip, limit=limit
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def create(
        self,
        title: Optional[str] = None,
        workspace_id: Optional[int] = None,
        rag_type: str = "vector",
    ) -> Result[ChatSession, DatabaseError]:
        """Create a new chat session.

        Args:
            title: Session title
            workspace_id: Workspace ID
            rag_type: RAG type

        Returns:
            Result with created session or database error
        """
        result = self.repository.create(title, workspace_id, rag_type)

        if hasattr(result, "unwrap"):
            session = result.unwrap()
            if self.cache and session:
                self._cache_session(session)
                # Invalidate workspace sessions list
                if workspace_id:
                    self.cache.delete(CacheKeys.workspace_chat_sessions(workspace_id))

        return result

    def update(self, session_id: int, **kwargs) -> Optional[ChatSession]:
        """Update session fields.

        Args:
            session_id: Session ID
            **kwargs: Fields to update

        Returns:
            Updated session or None
        """
        session = self.repository.update(session_id, **kwargs)
        if session:
            self._invalidate_cache(session_id)
            # Invalidate workspace sessions list if session has workspace
            if session.workspace_id and self.cache:
                self.cache.delete(CacheKeys.workspace_chat_sessions(session.workspace_id))
        return session

    def delete(self, session_id: int) -> bool:
        """Delete session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted successfully
        """
        # Get session to find workspace_id before deleting
        session = self.get_by_id(session_id)
        workspace_id = session.workspace_id if session else None

        result = self.repository.delete(session_id)
        if result:
            self._invalidate_cache(session_id)
            if workspace_id and self.cache:
                self.cache.delete(CacheKeys.workspace_chat_sessions(workspace_id))
        return result

    def _cache_session(self, session: ChatSession) -> None:
        """Cache session data.

        Args:
            session: ChatSession to cache
        """
        if not self.cache:
            return

        cache_key = CacheKeys.chat_session(session.id)
        cache_value = json.dumps(
            {
                "id": session.id,
                "workspace_id": session.workspace_id,
                "title": session.title,
                "rag_type": session.rag_type,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            }
        )
        self.cache.set(cache_key, cache_value, ttl=300)  # Cache for 5 minutes

    def _invalidate_cache(self, session_id: int) -> None:
        """Invalidate session cache.

        Args:
            session_id: Session ID to invalidate
        """
        if self.cache:
            cache_key = CacheKeys.chat_session(session_id)
            self.cache.delete(cache_key)
