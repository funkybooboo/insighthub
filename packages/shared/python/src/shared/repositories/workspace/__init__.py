"""Workspace repository module."""

from shared.repositories.workspace.sql_workspace_repository import SqlWorkspaceRepository
from shared.repositories.workspace.workspace_repository import WorkspaceRepository

__all__ = [
    "WorkspaceRepository",
    "SqlWorkspaceRepository",
]
