"""add_workspace_and_rag_config_tables

Revision ID: 3a98e52c2212
Revises: 0da33b00adf8
Create Date: 2025-11-19 14:21:20.994577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a98e52c2212'
down_revision: Union[str, None] = '0da33b00adf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspaces_user_id'), 'workspaces', ['user_id'], unique=False)

    # Create rag_configs table
    op.create_table(
        'rag_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), server_default='nomic-embed-text', nullable=False),
        sa.Column('embedding_dim', sa.Integer(), nullable=True),
        sa.Column('retriever_type', sa.String(length=50), server_default='vector', nullable=False),
        sa.Column('chunk_size', sa.Integer(), server_default='1000', nullable=False),
        sa.Column('chunk_overlap', sa.Integer(), server_default='200', nullable=False),
        sa.Column('top_k', sa.Integer(), server_default='8', nullable=False),
        sa.Column('rerank_enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('rerank_model', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id')
    )
    op.create_index(op.f('ix_rag_configs_workspace_id'), 'rag_configs', ['workspace_id'], unique=True)

    # Add workspace_id to documents table
    op.add_column('documents', sa.Column('workspace_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_documents_workspace_id'), 'documents', ['workspace_id'], unique=False)
    op.create_foreign_key(
        'fk_documents_workspace_id',
        'documents', 'workspaces',
        ['workspace_id'], ['id'],
        ondelete='CASCADE'
    )

    # Add workspace_id to chat_sessions table
    op.add_column('chat_sessions', sa.Column('workspace_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_chat_sessions_workspace_id'), 'chat_sessions', ['workspace_id'], unique=False)
    op.create_foreign_key(
        'fk_chat_sessions_workspace_id',
        'chat_sessions', 'workspaces',
        ['workspace_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Remove workspace_id from chat_sessions
    op.drop_constraint('fk_chat_sessions_workspace_id', 'chat_sessions', type_='foreignkey')
    op.drop_index(op.f('ix_chat_sessions_workspace_id'), table_name='chat_sessions')
    op.drop_column('chat_sessions', 'workspace_id')

    # Remove workspace_id from documents
    op.drop_constraint('fk_documents_workspace_id', 'documents', type_='foreignkey')
    op.drop_index(op.f('ix_documents_workspace_id'), table_name='documents')
    op.drop_column('documents', 'workspace_id')

    # Drop rag_configs table
    op.drop_index(op.f('ix_rag_configs_workspace_id'), table_name='rag_configs')
    op.drop_table('rag_configs')

    # Drop workspaces table
    op.drop_index(op.f('ix_workspaces_user_id'), table_name='workspaces')
    op.drop_table('workspaces')
