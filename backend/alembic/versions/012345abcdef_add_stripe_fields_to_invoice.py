"""Add stripe fields to invoice model

Revision ID: 012345abcdef
Revises: 21ec5b45cc17
Create Date: 2025-05-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012345abcdef'
down_revision = '21ec5b45cc17'  # Update this to the actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('invoice', sa.Column('stripe_checkout_session_id', sa.String(), nullable=True))
    op.add_column('invoice', sa.Column('stripe_payment_link', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('invoice', 'stripe_checkout_session_id')
    op.drop_column('invoice', 'stripe_payment_link')
