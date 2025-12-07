"""Chat message data access layer - coordinates cache and repository."""

import json
from datetime import datetime
from typing import Optional

from returns.result import Result

from src.cache_keys import CacheKeys
from src.domains.workspace.chat.message.models import ChatMessage
from src.domains.workspace.chat.message.repositories import ChatMessageRepository
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger
from src.infrastructure.types import DatabaseError, Pagination, PaginatedResult

logger = create_logger(__name__)


class ChatMessageDataAccess:
    """Data access layer for ChatMessage - handles caching + persistence."""

    def __init__(self, repository: ChatMessageRepository, cache: Optional[Cache] = None):
        """Initialize data access layer.

        Args:
            repository: ChatMessage repository for database operations
            cache: Optional cache for performance optimization
        """
        self.repository = repository  # Exposed for operations not handled by this layer
        self.cache = cache

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get message by ID with caching.

        Args:
            message_id: Chat message ID

        Returns:
            ChatMessage if found, None otherwise
        """
        # Try cache first
        cache_key = CacheKeys.chat_message(message_id)
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
                return ChatMessage(
                    id=data["id"],
                    session_id=data["session_id"],
                    role=data["role"],
                    content=data["content"],
                    extra_metadata=data.get("extra_metadata"),
                    created_at=(
                        datetime.fromisoformat(data["created_at"])
                        if data.get("created_at")
                        else datetime.utcnow()
                    ),
                )
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                logger.warning(f"Cache deserialization error for chat message {message_id}: {e}")

        # Cache miss - fetch from database
        message = self.repository.get_by_id(message_id)

        if message and self.cache:
            self._cache_message(message)

        return message

    def get_by_session(self, session_id: int, pagination: Pagination) -> PaginatedResult[ChatMessage]:
        """Get messages by session with caching.

        Args:
            session_id: Session ID
            pagination: Pagination parameters

        Returns:
            PaginatedResult of chat messages
        """
        # Try cache first for cache-eligible queries (first page, reasonable size)
        if pagination.is_cache_eligible():
            cache_key = CacheKeys.chat_session_messages(session_id)
            cached_json = self.cache.get(cache_key) if self.cache else None

            if cached_json:
                cached_result = self._try_get_cached_messages(cache_key, cached_json, pagination)
                if cached_result is not None:
                    return cached_result

        # Cache miss or pagination - fetch from database
        result = self.repository.get_by_session(session_id, pagination)

        # Cache the result for first page
        if self.cache and pagination.is_cache_eligible() and result.items:
            cache_value = json.dumps([m.id for m in result.items])
            self.cache.set(
                CacheKeys.chat_session_messages(session_id), cache_value, ttl=60
            )  # Cache for 1 minute
            # Also cache individual messages
            for message in result.items:
                self._cache_message(message)

        return result

    def _try_get_cached_messages(
        self, cache_key: str, cached_json: str, pagination: Pagination
    ) -> Optional[PaginatedResult[ChatMessage]]:
        """Try to retrieve messages from cache.

        Returns:
            PaginatedResult if all found, None if any missing or invalid
        """
        try:
            message_ids = json.loads(cached_json)
            messages = []
            skip, limit = pagination.offset_limit()
            for msg_id in message_ids[:limit]:
                msg = self.get_by_id(msg_id)
                if not msg:
                    if self.cache:
                        self.cache.delete(cache_key)
                    return None
                messages.append(msg)
            # Note: For cached results, we use the length as total_count
            # This is a simplification since we only cache first page
            return PaginatedResult(
                items=messages, total_count=len(message_ids), skip=skip, limit=limit
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: Optional[str] = None,
    ) -> Result[ChatMessage, DatabaseError]:
        """Create a new chat message.

        Args:
            session_id: Session ID
            role: Message role
            content: Message content
            extra_metadata: Optional metadata

        Returns:
            Result with created message or database error
        """
        result = self.repository.create(session_id, role, content, extra_metadata)

        if hasattr(result, "unwrap"):
            message = result.unwrap()
            if self.cache and message:
                self._cache_message(message)
                # Invalidate session messages list
                self.cache.delete(CacheKeys.chat_session_messages(session_id))

        return result

    def delete(self, message_id: int) -> bool:
        """Delete message.

        Args:
            message_id: Message ID

        Returns:
            True if deleted successfully
        """
        # Get message to find session_id before deleting
        message = self.get_by_id(message_id)
        session_id = message.session_id if message else None

        result = self.repository.delete(message_id)
        if result:
            self._invalidate_cache(message_id)
            if session_id and self.cache:
                self.cache.delete(CacheKeys.chat_session_messages(session_id))
        return result

    def _cache_message(self, message: ChatMessage) -> None:
        """Cache message data.

        Args:
            message: ChatMessage to cache
        """
        if not self.cache:
            return

        cache_key = CacheKeys.chat_message(message.id)
        cache_value = json.dumps(
            {
                "id": message.id,
                "session_id": message.session_id,
                "role": message.role,
                "content": message.content,
                "extra_metadata": message.extra_metadata,
                "created_at": message.created_at.isoformat() if message.created_at else None,
            }
        )
        self.cache.set(cache_key, cache_value, ttl=300)  # Cache for 5 minutes

    def _invalidate_cache(self, message_id: int) -> None:
        """Invalidate message cache.

        Args:
            message_id: Message ID to invalidate
        """
        if self.cache:
            cache_key = CacheKeys.chat_message(message_id)
            self.cache.delete(cache_key)
