"""Renamed table user to user_mobile

Revision ID: 06b31b1e9add
Revises: c27b8c0a8123
Create Date: 2025-11-06 07:07:50.592177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06b31b1e9add'
down_revision: Union[str, Sequence[str], None] = 'c27b8c0a8123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraints first
    op.drop_constraint('address_user_id_fkey', 'address', type_='foreignkey')
    op.drop_constraint('result_user_id_fkey', 'result', type_='foreignkey')
    
    # Rename the table
    op.rename_table('user', 'user_mobile')
    
    # Recreate foreign key constraints pointing to the renamed table
    op.create_foreign_key('address_user_id_fkey', 'address', 'user_mobile', ['user_id'], ['id'])
    op.create_foreign_key('result_user_id_fkey', 'result', 'user_mobile', ['user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraints
    op.drop_constraint('result_user_id_fkey', 'result', type_='foreignkey')
    op.drop_constraint('address_user_id_fkey', 'address', type_='foreignkey')
    
    # Rename the table back
    op.rename_table('user_mobile', 'user')
    
    # Recreate foreign key constraints pointing to the original table name
    op.create_foreign_key('address_user_id_fkey', 'address', 'user', ['user_id'], ['id'])
    op.create_foreign_key('result_user_id_fkey', 'result', 'user', ['user_id'], ['id'], ondelete='SET NULL')
