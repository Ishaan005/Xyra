"""Add missing columns from revised schema

Revision ID: facc40e7b78d
Revises: 21ec5b45cc17
Create Date: 2025-05-28 17:00:54.683501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'facc40e7b78d'
down_revision: Union[str, None] = '21ec5b45cc17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('agent', sa.Column('status', sa.String(length=50), nullable=False, server_default='active'))
    op.add_column('agent', sa.Column('type', sa.String(length=100), nullable=True))
    op.add_column('agent', sa.Column('capabilities', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('organization', sa.Column('external_id', sa.String(length=255), nullable=True))
    op.add_column('organization', sa.Column('status', sa.String(length=50), nullable=False, server_default='active'))
    op.add_column('organization', sa.Column('billing_email', sa.String(length=255), nullable=True))
    op.add_column('organization', sa.Column('contact_name', sa.String(length=255), nullable=True))
    op.add_column('organization', sa.Column('contact_phone', sa.String(length=50), nullable=True))
    op.add_column('organization', sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'))
    op.add_column('organization', sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'))
    op.create_unique_constraint('uq_organization_external_id', 'organization', ['external_id'])
    op.add_column('user', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user', sa.Column('role', sa.String(length=50), nullable=False, server_default='user'))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    op.drop_column('user', 'last_login')
    op.drop_constraint('uq_organization_external_id', 'organization', type_='unique')
    op.drop_column('organization', 'settings')
    op.drop_column('organization', 'timezone')
    op.drop_column('organization', 'contact_phone')
    op.drop_column('organization', 'contact_name')
    op.drop_column('organization', 'billing_email')
    op.drop_column('organization', 'status')
    op.drop_column('organization', 'external_id')
    op.drop_column('agent', 'capabilities')
    op.drop_column('agent', 'type')
    op.drop_column('agent', 'status')
    # ### end Alembic commands ###
