"""Mappers for workspace domain."""

from typing import List

from src.domains.workspace.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace
from src.infrastructure.mappers import map_timestamps

from .dtos import (
    GraphRagConfigResponse,
    RagConfigResponse,
    VectorRagConfigResponse,
    WorkspaceListResponse,
    WorkspaceResponse,
)


class WorkspaceMapper:
    """Mapper for converting between Workspace models and Response DTOs."""

    @staticmethod
    def to_response(workspace: Workspace) -> WorkspaceResponse:
        """
        Convert Workspace model to Response DTO.

        Args:
            workspace: Workspace model instance

        Returns:
            WorkspaceResponse instance
        """
        created_at_str, updated_at_str = map_timestamps(workspace.created_at, workspace.updated_at)
        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            rag_type=workspace.rag_type,
            status=workspace.status,
            created_at=created_at_str,
            updated_at=updated_at_str,
        )

    @staticmethod
    def to_list_response(workspaces: List[Workspace]) -> WorkspaceListResponse:
        """
        Convert list of Workspace models to WorkspaceListResponse.

        Args:
            workspaces: List of Workspace model instances

        Returns:
            WorkspaceListResponse instance
        """
        return WorkspaceListResponse(
            workspaces=[WorkspaceMapper.to_response(w) for w in workspaces]
        )


class VectorRagConfigMapper:
    """Mapper for VectorRagConfig models and Response DTOs."""

    @staticmethod
    def to_response(config: VectorRagConfig) -> VectorRagConfigResponse:
        """
        Convert VectorRagConfig model to Response DTO.

        Args:
            config: VectorRagConfig model instance

        Returns:
            VectorRagConfigResponse instance
        """
        return VectorRagConfigResponse(
            embedding_algorithm=config.embedding_algorithm,
            chunking_algorithm=config.chunking_algorithm,
            rerank_algorithm=config.rerank_algorithm,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            top_k=config.top_k,
        )


class GraphRagConfigMapper:
    """Mapper for GraphRagConfig models and Response DTOs."""

    @staticmethod
    def to_response(config: GraphRagConfig) -> GraphRagConfigResponse:
        """
        Convert GraphRagConfig model to Response DTO.

        Args:
            config: GraphRagConfig model instance

        Returns:
            GraphRagConfigResponse instance
        """
        return GraphRagConfigResponse(
            entity_extraction_algorithm=config.entity_extraction_algorithm,
            relationship_extraction_algorithm=config.relationship_extraction_algorithm,
            clustering_algorithm=config.clustering_algorithm,
        )


class RagConfigMapper:
    """Mapper for RagConfig models and Response DTOs."""

    @staticmethod
    def to_response(config: RagConfig) -> RagConfigResponse:
        """
        Convert RagConfig model to Response DTO.

        Args:
            config: RagConfig model instance

        Returns:
            RagConfigResponse instance
        """
        return RagConfigResponse(
            workspace_id=config.workspace_id,
            rag_type=config.rag_type,
            config=config.config,
        )
