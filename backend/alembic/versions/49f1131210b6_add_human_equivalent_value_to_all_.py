"""Add human_equivalent_value to all billing configs

Revision ID: 49f1131210b6
Revises: 947ebf5f1bb2
Create Date: 2025-07-20 19:36:11.490108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49f1131210b6'
down_revision: Union[str, None] = '947ebf5f1bb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add human_equivalent_value to all billing config tables."""
    # Add to AgentBasedConfig
    op.add_column('agentbasedconfig', sa.Column('human_equivalent_value', sa.Float(), nullable=True, default=0.0))
    
    # Add to ActivityBasedConfig
    op.add_column('activitybasedconfig', sa.Column('human_equivalent_value', sa.Float(), nullable=True, default=0.0))
    
    # Add to OutcomeBasedConfig
    op.add_column('outcomebasedconfig', sa.Column('human_equivalent_value', sa.Float(), nullable=True, default=0.0))
    
    # Add to WorkflowBasedConfig
    op.add_column('workflowbasedconfig', sa.Column('human_equivalent_value', sa.Float(), nullable=True, default=0.0))
    
    # Add to WorkflowType
    op.add_column('workflowtype', sa.Column('human_equivalent_value', sa.Float(), nullable=True, default=0.0))


def downgrade() -> None:
    """Remove human_equivalent_value from all billing config tables."""
    # Remove from WorkflowType
    op.drop_column('workflowtype', 'human_equivalent_value')
    
    # Remove from WorkflowBasedConfig
    op.drop_column('workflowbasedconfig', 'human_equivalent_value')
    
    # Remove from OutcomeBasedConfig
    op.drop_column('outcomebasedconfig', 'human_equivalent_value')
    
    # Remove from ActivityBasedConfig
    op.drop_column('activitybasedconfig', 'human_equivalent_value')
    
    # Remove from AgentBasedConfig
    op.drop_column('agentbasedconfig', 'human_equivalent_value')
