"""add_password_hash_to_users

Revision ID: a20aea937c13
Revises: 
Create Date: 2025-11-11 19:50:38.354658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a20aea937c13'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password_hash column to users table
    # Making it nullable initially to handle existing users
    op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove password_hash column from users table
    op.drop_column('users', 'password_hash')
