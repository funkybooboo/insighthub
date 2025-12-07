"""Centralized cache key generation.

This module provides a single source of truth for all cache key formats
used throughout the application. All cache keys follow a consistent
colon-separated pattern: namespace:entity:id[:suffix]
"""


class CacheKeys:
    """Centralized cache key generation."""

    NAMESPACE = "insighthub"

    @classmethod
    def workspaces_all(cls) -> str:
        """Cache key for all workspaces list.

        Returns:
            Cache key in format: workspaces:all
        """
        return "workspaces:all"

    @classmethod
    def workspace(cls, workspace_id: int) -> str:
        """Cache key for workspace entity.

        Args:
            workspace_id: Workspace ID

        Returns:
            Cache key in format: insighthub:workspace:{workspace_id}
        """
        return f"workspace:{workspace_id}"

    @classmethod
    def workspace_vector_config(cls, workspace_id: int) -> str:
        """Cache key for workspace Vector RAG config.

        Args:
            workspace_id: Workspace ID

        Returns:
            Cache key in format: insighthub:workspace:{workspace_id}:vector_rag_config
        """
        return f"workspace:{workspace_id}:vector_rag_config"

    @classmethod
    def workspace_graph_config(cls, workspace_id: int) -> str:
        """Cache key for workspace Graph RAG config.

        Args:
            workspace_id: Workspace ID

        Returns:
            Cache key in format: insighthub:workspace:{workspace_id}:graph_rag_config
        """
        return f"workspace:{workspace_id}:graph_rag_config"

    @classmethod
    def workspace_documents(cls, workspace_id: int) -> str:
        """Cache key for workspace documents list.

        Args:
            workspace_id: Workspace ID

        Returns:
            Cache key in format: insighthub:workspace:{workspace_id}:documents
        """
        return f"workspace:{workspace_id}:documents"

    @classmethod
    def workspace_chat_sessions(cls, workspace_id: int) -> str:
        """Cache key for workspace chat sessions list.

        Args:
            workspace_id: Workspace ID

        Returns:
            Cache key in format: insighthub:workspace:{workspace_id}:chat_sessions
        """
        return f"workspace:{workspace_id}:chat_sessions"

    @classmethod
    def document(cls, document_id: int) -> str:
        """Cache key for document entity.

        Args:
            document_id: Document ID

        Returns:
            Cache key in format: insighthub:document:{document_id}
        """
        return f"document:{document_id}"

    @classmethod
    def chat_session(cls, session_id: int) -> str:
        """Cache key for chat session entity.

        Args:
            session_id: Session ID

        Returns:
            Cache key in format: insighthub:chat_session:{session_id}
        """
        return f"chat_session:{session_id}"

    @classmethod
    def chat_session_messages(cls, session_id: int) -> str:
        """Cache key for session messages list.

        Args:
            session_id: Session ID

        Returns:
            Cache key in format: insighthub:session:{session_id}:chat_messages
        """
        return f"session:{session_id}:chat_messages"

    @classmethod
    def chat_message(cls, message_id: int) -> str:
        """Cache key for chat message entity.

        Args:
            message_id: Message ID

        Returns:
            Cache key in format: insighthub:chat_message:{message_id}
        """
        return f"chat_message:{message_id}"
