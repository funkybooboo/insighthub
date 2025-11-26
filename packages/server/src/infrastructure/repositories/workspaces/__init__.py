"""Workspaces repository module."""

from .factory import create_workspace_repository
from .in_memory_workspace_repository import InMemoryWorkspaceRepository
from .workspace_repository import WorkspaceRepository

__all__ = ["WorkspaceRepository", "InMemoryWorkspaceRepository", "create_workspace_repository"]
