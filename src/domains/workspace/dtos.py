"""DTOs for workspace domain."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.infrastructure.rag.options import get_valid_rag_types, is_valid_rag_type

# ============================================================================
# Request DTOs (User Input) - Pydantic models with validation
# ============================================================================


class CreateWorkspaceRequest(BaseModel):
    """Request DTO for workspace creation with validation."""

    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    description: Optional[str] = Field(None, max_length=1000, description="Workspace description")
    rag_type: Optional[str] = Field(None, description="RAG type (vector, graph, hybrid)")

    # Vector RAG configuration
    chunking_algorithm: Optional[str] = Field(None, description="Chunking algorithm")
    chunk_size: Optional[int] = Field(None, ge=1, description="Chunk size")
    chunk_overlap: Optional[int] = Field(None, ge=0, description="Chunk overlap")
    embedding_algorithm: Optional[str] = Field(None, description="Embedding algorithm")
    top_k: Optional[int] = Field(None, ge=1, description="Top K results")
    rerank_algorithm: Optional[str] = Field(None, description="Reranking algorithm")

    # Graph RAG configuration
    entity_extraction_algorithm: Optional[str] = Field(None, description="Entity extraction algorithm")
    relationship_extraction_algorithm: Optional[str] = Field(
        None, description="Relationship extraction algorithm"
    )
    clustering_algorithm: Optional[str] = Field(None, description="Clustering algorithm")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean name."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Workspace name cannot be empty")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v is None:
            return None
        cleaned = v.strip()
        return cleaned if cleaned else None

    @field_validator("rag_type")
    @classmethod
    def validate_rag_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate RAG type if provided."""
        if v is None:
            return None
        if not is_valid_rag_type(v):
            valid_types = get_valid_rag_types()
            raise ValueError(f"Invalid rag_type. Must be one of: {', '.join(valid_types)}")
        return v

    model_config = {"str_strip_whitespace": True, "validate_assignment": True}


class UpdateWorkspaceRequest(BaseModel):
    """Request DTO for workspace update with validation."""

    workspace_id: int = Field(..., gt=0, description="Workspace ID")
    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="New workspace name"
    )
    description: Optional[str] = Field(None, max_length=1000, description="New description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean name if provided."""
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Workspace name cannot be empty")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description if provided."""
        if v is None:
            return None
        cleaned = v.strip()
        return cleaned if cleaned else None

    model_config = {"str_strip_whitespace": True, "validate_assignment": True}


class DeleteWorkspaceRequest(BaseModel):
    """Request DTO for workspace deletion with validation."""

    workspace_id: int = Field(..., gt=0, description="Workspace ID to delete")


class ShowWorkspaceRequest(BaseModel):
    """Request DTO for showing workspace details with validation."""

    workspace_id: int = Field(..., gt=0, description="Workspace ID to show")


class SelectWorkspaceRequest(BaseModel):
    """Request DTO for selecting a workspace with validation."""

    workspace_id: int = Field(..., gt=0, description="Workspace ID to select")


# ============================================================================
# Response DTOs (Service Output) - Pydantic models for consistent serialization
# ============================================================================


class WorkspaceResponse(BaseModel):
    """Response DTO for single workspace."""

    id: int
    name: str
    description: Optional[str]
    rag_type: str
    status: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class WorkspaceListResponse(BaseModel):
    """Response DTO for workspace list."""

    workspaces: list[WorkspaceResponse]


class VectorRagConfigResponse(BaseModel):
    """Response DTO for vector RAG configuration."""

    embedding_algorithm: str
    chunking_algorithm: str
    rerank_algorithm: str
    chunk_size: int
    chunk_overlap: int
    top_k: int

    model_config = {"from_attributes": True}


class GraphRagConfigResponse(BaseModel):
    """Response DTO for graph RAG configuration."""

    entity_extraction_algorithm: str
    relationship_extraction_algorithm: str
    clustering_algorithm: str

    model_config = {"from_attributes": True}


class RagConfigResponse(BaseModel):
    """Response DTO for generic RAG configuration."""

    workspace_id: int
    rag_type: str
    config: dict

    model_config = {"from_attributes": True}
