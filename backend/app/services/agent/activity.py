"""
Activity operations for agents.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.agent import AgentActivity as AgentActivityModel, AgentCost as AgentCostModel
from app.schemas.agent import AgentActivityCreate
from app.services.billing_model.calculation import calculate_cost
from .core import get_agent

logger = logging.getLogger(__name__)


def record_agent_activity(db: Session, activity_in: AgentActivityCreate) -> AgentActivityModel:
    """
    Record an activity for an agent
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=activity_in.agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {activity_in.agent_id} not found")
    
    # Create activity
    activity = AgentActivityModel(
        agent_id=activity_in.agent_id,
        activity_type=activity_in.activity_type,
        timestamp=datetime.now(timezone.utc),
        activity_metadata=activity_in.activity_metadata,
    )
    
    # Add activity to database
    db.add(activity)
    db.commit()
    db.refresh(activity)
    # Update agent's last active timestamp
    setattr(agent, 'last_active', datetime.now(timezone.utc))
    db.commit()

    logger.info(f"Recorded activity {activity.activity_type} for agent: {agent.name}")
    # Auto-record cost for activity based on billing model
    bm = agent.billing_model
    if bm and bm.model_type == "activity":
        # For activity-based billing, use activity_type from the config
        if bm.model_type == "activity":
            # Find matching activity config based on activity_type
            activity_configs = bm.activity_config or []
            matching_config = None
            for cfg in activity_configs:
                if cfg.activity_type == activity.activity_type:
                    matching_config = cfg
                    break
            
            if matching_config:
                # Use specific activity config for calculation
                usage_data = {"units": 1, "activity_type": activity.activity_type}
                cost_amt = calculate_cost(bm, usage_data)
                
                # Create cost entry with enhanced details
                cost_entry = AgentCostModel(
                    agent_id=agent.id,
                    cost_type="activity",
                    amount=cost_amt,
                    currency="USD",
                    timestamp=datetime.now(timezone.utc),
                    details={
                        "activity_id": activity.id, 
                        "activity_type": activity.activity_type,
                        "unit_type": matching_config.unit_type,
                        "price_per_unit": matching_config.price_per_unit,
                        "volume_pricing_enabled": matching_config.volume_pricing_enabled,
                        "billing_frequency": matching_config.billing_frequency
                    }
                )
                db.add(cost_entry)
                db.commit()
                logger.info(f"Auto-recorded activity cost {cost_amt} USD for agent: {agent.name}")
            else:
                logger.warning(f"No matching activity config found for activity type: {activity.activity_type}")
        else:
            logger.warning(f"Unsupported model type for activity tracking: {bm.model_type}")
            
            cost_entry = AgentCostModel(
                agent_id=agent.id,
                cost_type="activity",
                amount=0.0,
                currency="USD",
                timestamp=datetime.now(timezone.utc),
                details={"activity_id": activity.id, "activity_type": activity.activity_type}
            )
            db.add(cost_entry)
            db.commit()
            logger.info(f"Auto-recorded activity cost 0.0 USD for agent: {agent.name}")
    return activity
