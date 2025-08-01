"""Add API key table for organization-scoped API keys

Revision ID: c4efdbbf0fb6
Revises: 49f1131210b6
Create Date: 2025-07-23 08:08:45.094032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4efdbbf0fb6'
down_revision: Union[str, None] = '49f1131210b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create API key table for organization-scoped API keys
    op.create_table('apikey',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('key_hash', sa.String(length=255), nullable=False),
    sa.Column('key_prefix', sa.String(length=20), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('permissions', sa.Text(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key_hash')
    )
    op.create_index(op.f('ix_apikey_id'), 'apikey', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove API key table
    op.drop_index(op.f('ix_apikey_id'), table_name='apikey')
    op.drop_table('apikey')
