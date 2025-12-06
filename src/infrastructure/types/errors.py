"""Error types for the application."""

from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationError:
    """Error for validation failures."""

    message: str
    field: Optional[str]= None


@dataclass(frozen=True)
class NotFoundError:
    """Error for resource not found."""

    resource: str
    id: int | str


@dataclass(frozen=True)
class WorkflowError:
    """Error from RAG workflow execution."""

    message: str
    workflow: str


@dataclass(frozen=True)
class DatabaseError:
    """Error from database operations."""

    message: str
    operation: str


@dataclass(frozen=True)
class StorageError:
    """Error from storage operations."""

    message: str
    operation: str


@dataclass(frozen=True)
class VectorStoreError:
    """Error from vector store operations."""

    message: str
    operation: str
