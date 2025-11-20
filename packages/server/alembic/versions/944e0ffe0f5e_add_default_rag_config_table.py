"""add_default_rag_config_table

Revision ID: 944e0ffe0f5e
Revises: 3a98e52c2212
Create Date: 2025-11-19 14:26:02.693537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '944e0ffe0f5e'
down_revision: Union[str, None] = '3a98e52c2212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create default_rag_configs table
    op.create_table(
        "default_rag_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), server_default="nomic-embed-text", nullable=False),
        sa.Column("embedding_dim", sa.Integer(), nullable=True),
        sa.Column("retriever_type", sa.String(length=50), server_default="vector", nullable=False),
        sa.Column("chunk_size", sa.Integer(), server_default="1000", nullable=False),
        sa.Column("chunk_overlap", sa.Integer(), server_default="200", nullable=False),
        sa.Column("top_k", sa.Integer(), server_default="8", nullable=False),
        sa.Column("rerank_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("rerank_model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_default_rag_configs_user_id"), "default_rag_configs", ["user_id"], unique=True)


def downgrade() -> None:
    # Drop default_rag_configs table
    op.drop_index(op.f("ix_default_rag_configs_user_id"), table_name="default_rag_configs")
    op.drop_table("default_rag_configs")
