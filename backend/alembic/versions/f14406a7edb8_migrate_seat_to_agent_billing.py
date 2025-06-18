"""migrate_seat_to_agent_billing

Revision ID: f14406a7edb8
Revises: 5331bdb51fd7
Create Date: 2025-06-16 17:34:14.865663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f14406a7edb8'
down_revision: Union[str, None] = '5331bdb51fd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Convert seatbasedconfig to agentbasedconfig."""
    
    # Create new agentbasedconfig table with all the agent-based billing fields
    op.create_table('agentbasedconfig',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('billing_model_id', sa.Integer(), nullable=False),
        sa.Column('base_agent_fee', sa.Float(), nullable=False),
        sa.Column('billing_frequency', sa.String(), nullable=False),
        sa.Column('setup_fee', sa.Float(), nullable=True),
        sa.Column('volume_discount_enabled', sa.Boolean(), nullable=True),
        sa.Column('volume_discount_threshold', sa.Integer(), nullable=True),
        sa.Column('volume_discount_percentage', sa.Float(), nullable=True),
        sa.Column('agent_tier', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['billing_model_id'], ['billingmodel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on billing_model_id for performance
    op.create_index(op.f('ix_agentbasedconfig_billing_model_id'), 'agentbasedconfig', ['billing_model_id'], unique=False)
    
    # Migrate existing data from seatbasedconfig to agentbasedconfig
    # Map seat pricing to agent pricing (seat price becomes base agent fee)
    op.execute("""
        INSERT INTO agentbasedconfig (
            created_at, updated_at, billing_model_id, base_agent_fee, 
            billing_frequency, setup_fee, volume_discount_enabled, 
            volume_discount_threshold, volume_discount_percentage, agent_tier
        )
        SELECT 
            created_at, updated_at, billing_model_id, price_per_seat as base_agent_fee,
            billing_frequency, 0.0 as setup_fee, false as volume_discount_enabled,
            NULL as volume_discount_threshold, NULL as volume_discount_percentage,
            'professional' as agent_tier
        FROM seatbasedconfig
    """)
    
    # Update billing model types from 'seat' to 'agent'
    op.execute("UPDATE billingmodel SET model_type = 'agent' WHERE model_type = 'seat'")
    
    # Drop the old seatbasedconfig table
    op.drop_table('seatbasedconfig')


def downgrade() -> None:
    """Downgrade schema: Convert agentbasedconfig back to seatbasedconfig."""
    
    # Create the old seatbasedconfig table
    op.create_table('seatbasedconfig',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('billing_model_id', sa.Integer(), nullable=False),
        sa.Column('price_per_seat', sa.Float(), nullable=False),
        sa.Column('billing_frequency', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['billing_model_id'], ['billingmodel.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate data back from agentbasedconfig to seatbasedconfig
    # Map agent pricing back to seat pricing (base agent fee becomes seat price)
    op.execute("""
        INSERT INTO seatbasedconfig (
            created_at, updated_at, billing_model_id, price_per_seat, billing_frequency
        )
        SELECT 
            created_at, updated_at, billing_model_id, base_agent_fee as price_per_seat, billing_frequency
        FROM agentbasedconfig
    """)
    
    # Update billing model types from 'agent' back to 'seat'
    op.execute("UPDATE billingmodel SET model_type = 'seat' WHERE model_type = 'agent'")
    
    # Drop the agentbasedconfig table
    op.drop_index(op.f('ix_agentbasedconfig_billing_model_id'), table_name='agentbasedconfig')
    op.drop_table('agentbasedconfig')
