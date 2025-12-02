"""DTOs for workspace domain."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WorkspaceDTO:
    """DTO for workspace responses (single-user system)."""

    id: int
    name: str
    description: Optional[str]
    rag_type: str
    status: str
    created_at: str
    updated_at: str


@dataclass
class WorkspaceListDTO:
    """DTO for workspace list responses."""

    workspaces: List[WorkspaceDTO]


@dataclass
class VectorRagConfigDTO:
    """DTO for vector RAG configuration responses."""

    embedding_algorithm: str
    chunking_algorithm: str
    rerank_algorithm: str
    chunk_size: int
    chunk_overlap: int
    top_k: int


@dataclass
class GraphRagConfigDTO:
    """DTO for graph RAG configuration responses."""

    entity_extraction_algorithm: str
    relationship_extraction_algorithm: str
    clustering_algorithm: str


@dataclass
class RagConfigDTO:
    """DTO for generic RAG configuration responses."""

    workspace_id: int
    rag_type: str
    config: dict


@dataclass
class CreateWorkspaceDTO:
    """DTO for workspace creation requests."""

    name: str
    description: Optional[str] = None
    rag_type: str = "vector"
    rag_config: Optional[dict] = None


@dataclass
class UpdateWorkspaceDTO:
    """DTO for workspace update requests."""

    name: Optional[str] = None
    description: Optional[str] = None
