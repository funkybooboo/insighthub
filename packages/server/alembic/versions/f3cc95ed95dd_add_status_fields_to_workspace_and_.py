"""add_status_fields_to_workspace_and_document

Revision ID: f3cc95ed95dd
Revises: 944e0ffe0f5e
Create Date: 2025-11-19 14:29:54.040353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3cc95ed95dd'
down_revision: Union[str, None] = '944e0ffe0f5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add status fields to workspaces table
    op.add_column('workspaces', sa.Column('status', sa.String(length=50), server_default='provisioning', nullable=False))
    op.add_column('workspaces', sa.Column('status_message', sa.Text(), nullable=True))
    op.create_index(op.f('ix_workspaces_status'), 'workspaces', ['status'], unique=False)

    # Add processing status fields to documents table
    op.add_column('documents', sa.Column('processing_status', sa.String(length=50), server_default='pending', nullable=False))
    op.add_column('documents', sa.Column('processing_error', sa.Text(), nullable=True))
    op.create_index(op.f('ix_documents_processing_status'), 'documents', ['processing_status'], unique=False)


def downgrade() -> None:
    # Drop document processing status fields
    op.drop_index(op.f('ix_documents_processing_status'), table_name='documents')
    op.drop_column('documents', 'processing_error')
    op.drop_column('documents', 'processing_status')

    # Drop workspace status fields
    op.drop_index(op.f('ix_workspaces_status'), table_name='workspaces')
    op.drop_column('workspaces', 'status_message')
    op.drop_column('workspaces', 'status')
