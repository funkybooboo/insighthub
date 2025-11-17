"""add_theme_preference_to_users

Revision ID: 0da33b00adf8
Revises: a20aea937c13
Create Date: 2025-11-16 21:22:05.251181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0da33b00adf8'
down_revision: Union[str, None] = 'a20aea937c13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('theme_preference', sa.String(length=10), nullable=False, server_default='dark'))


def downgrade() -> None:
    op.drop_column('users', 'theme_preference')
