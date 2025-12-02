"""Mappers for workspace domain."""

from typing import List

from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace

from .dtos import (
    GraphRagConfigDTO,
    RagConfigDTO,
    VectorRagConfigDTO,
    WorkspaceDTO,
    WorkspaceListDTO,
)


class WorkspaceMapper:
    """Mapper for converting between Workspace models and DTOs."""

    @staticmethod
    def to_dto(workspace: Workspace) -> WorkspaceDTO:
        """
        Convert Workspace model to DTO (single-user system).

        Args:
            workspace: Workspace model instance

        Returns:
            WorkspaceDTO instance
        """
        return WorkspaceDTO(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            rag_type=workspace.rag_type,
            status=workspace.status,
            created_at=workspace.created_at.isoformat(),
            updated_at=workspace.updated_at.isoformat(),
        )

    @staticmethod
    def to_dto_list(workspaces: List[Workspace]) -> WorkspaceListDTO:
        """
        Convert list of Workspace models to WorkspaceListDTO.

        Args:
            workspaces: List of Workspace model instances

        Returns:
            WorkspaceListDTO instance
        """
        return WorkspaceListDTO(workspaces=[WorkspaceMapper.to_dto(w) for w in workspaces])

    @staticmethod
    def dto_to_dict(dto: WorkspaceDTO) -> dict:
        """
        Convert WorkspaceDTO to dictionary for JSON response (single-user system).

        Args:
            dto: WorkspaceDTO instance

        Returns:
            Dictionary representation
        """
        return {
            "id": dto.id,
            "name": dto.name,
            "description": dto.description,
            "rag_type": dto.rag_type,
            "status": dto.status,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        }

    @staticmethod
    def dto_list_to_dict(dto_list: WorkspaceListDTO) -> List[dict]:
        """
        Convert WorkspaceListDTO to list of dictionaries.

        Args:
            dto_list: WorkspaceListDTO instance

        Returns:
            List of dictionary representations
        """
        return [WorkspaceMapper.dto_to_dict(dto) for dto in dto_list.workspaces]


class VectorRagConfigMapper:
    """Mapper for VectorRagConfig models and DTOs."""

    @staticmethod
    def to_dto(config: VectorRagConfig) -> VectorRagConfigDTO:
        """
        Convert VectorRagConfig model to DTO.

        Args:
            config: VectorRagConfig model instance

        Returns:
            VectorRagConfigDTO instance
        """
        return VectorRagConfigDTO(
            embedding_algorithm=config.embedding_algorithm,
            chunking_algorithm=config.chunking_algorithm,
            rerank_algorithm=config.rerank_algorithm,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            top_k=config.top_k,
        )

    @staticmethod
    def dto_to_dict(dto: VectorRagConfigDTO) -> dict:
        """
        Convert VectorRagConfigDTO to dictionary.

        Args:
            dto: VectorRagConfigDTO instance

        Returns:
            Dictionary representation
        """
        return {
            "embedding_algorithm": dto.embedding_algorithm,
            "chunking_algorithm": dto.chunking_algorithm,
            "rerank_algorithm": dto.rerank_algorithm,
            "chunk_size": dto.chunk_size,
            "chunk_overlap": dto.chunk_overlap,
            "top_k": dto.top_k,
        }


class GraphRagConfigMapper:
    """Mapper for GraphRagConfig models and DTOs."""

    @staticmethod
    def to_dto(config: GraphRagConfig) -> GraphRagConfigDTO:
        """
        Convert GraphRagConfig model to DTO.

        Args:
            config: GraphRagConfig model instance

        Returns:
            GraphRagConfigDTO instance
        """
        return GraphRagConfigDTO(
            entity_extraction_algorithm=config.entity_extraction_algorithm,
            relationship_extraction_algorithm=config.relationship_extraction_algorithm,
            clustering_algorithm=config.clustering_algorithm,
        )

    @staticmethod
    def dto_to_dict(dto: GraphRagConfigDTO) -> dict:
        """
        Convert GraphRagConfigDTO to dictionary.

        Args:
            dto: GraphRagConfigDTO instance

        Returns:
            Dictionary representation
        """
        return {
            "entity_extraction_algorithm": dto.entity_extraction_algorithm,
            "relationship_extraction_algorithm": dto.relationship_extraction_algorithm,
            "clustering_algorithm": dto.clustering_algorithm,
        }


class RagConfigMapper:
    """Mapper for RagConfig models and DTOs."""

    @staticmethod
    def to_dto(config: RagConfig) -> RagConfigDTO:
        """
        Convert RagConfig model to DTO.

        Args:
            config: RagConfig model instance

        Returns:
            RagConfigDTO instance
        """
        return RagConfigDTO(
            workspace_id=config.workspace_id,
            rag_type=config.rag_type,
            config=config.config,
        )

    @staticmethod
    def dto_to_dict(dto: RagConfigDTO) -> dict:
        """
        Convert RagConfigDTO to dictionary.

        Args:
            dto: RagConfigDTO instance

        Returns:
            Dictionary representation
        """
        return {
            "workspace_id": dto.workspace_id,
            "rag_type": dto.rag_type,
            "config": dto.config,
        }
