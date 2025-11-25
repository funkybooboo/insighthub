"""Entity repository module."""

from shared.repositories.graph_rag.entity.entity_repository import EntityRepository
from shared.repositories.graph_rag.entity.factory import create_entity_repository
from shared.repositories.graph_rag.entity.sql_entity_repository import SqlEntityRepository

__all__ = [
    "EntityRepository",
    "SqlEntityRepository",
    "create_entity_repository",
]