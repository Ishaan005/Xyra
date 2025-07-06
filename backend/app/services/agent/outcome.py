"""
Outcome operations for agents.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.agent import AgentOutcome as AgentOutcomeModel, AgentCost as AgentCostModel
from app.schemas.agent import AgentOutcomeCreate
from app.services.billing_model.calculation import calculate_cost
from .core import get_agent

logger = logging.getLogger(__name__)


def record_agent_outcome(db: Session, outcome_in: AgentOutcomeCreate) -> AgentOutcomeModel:
    """
    Record an outcome for an agent
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=outcome_in.agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {outcome_in.agent_id} not found")
    
    # Create outcome
    outcome = AgentOutcomeModel(
        agent_id=outcome_in.agent_id,
        outcome_type=outcome_in.outcome_type,
        value=outcome_in.value,
        currency=outcome_in.currency,
        timestamp=datetime.now(timezone.utc),
        details=outcome_in.details,
        verified=outcome_in.verified,
    )
    
    # Add outcome to database
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    logger.info(f"Recorded outcome {outcome.value} {outcome.currency} for agent: {agent.name}")
    # Auto-record cost for outcome based on billing model
    bm = agent.billing_model
    if bm and bm.model_type == "outcome":
        # For outcome-based billing, use outcome_type from the config
        if bm.model_type == "outcome":
            # Find matching outcome config based on outcome_type
            outcome_configs = bm.outcome_config or []
            matching_config = None
            for cfg in outcome_configs:
                if cfg.outcome_type == outcome.outcome_type:
                    matching_config = cfg
                    break
            
            if matching_config:
                # Use specific outcome config for calculation
                usage_data = {"outcome_value": outcome.value, "outcome_type": outcome.outcome_type}
                cost_amt = calculate_cost(bm, usage_data)
                
                # Create cost entry with enhanced details
                cost_entry = AgentCostModel(
                    agent_id=agent.id,
                    cost_type="outcome",
                    amount=cost_amt,
                    currency=outcome.currency,
                    timestamp=datetime.now(timezone.utc),
                    details={
                        "outcome_id": outcome.id, 
                        "outcome_type": outcome.outcome_type,
                        "outcome_name": matching_config.outcome_name,
                        "base_platform_fee": matching_config.base_platform_fee,
                        "percentage": matching_config.percentage,
                        "attribution_window_days": matching_config.attribution_window_days,
                        "requires_verification": matching_config.requires_verification,
                        "verified": outcome.verified,
                        "risk_premium_percentage": matching_config.risk_premium_percentage
                    }
                )
                db.add(cost_entry)
                db.commit()
                logger.info(f"Auto-recorded outcome cost {cost_amt} {outcome.currency} for agent: {agent.name}")
            else:
                logger.warning(f"No matching outcome config found for outcome type: {outcome.outcome_type}")
        else:
            logger.warning(f"Unsupported model type for outcome tracking: {bm.model_type}")
            
            cost_entry = AgentCostModel(
                agent_id=agent.id,
                cost_type="outcome",
                amount=0.0,
                currency=outcome.currency,
                timestamp=datetime.now(timezone.utc),
                details={"outcome_id": outcome.id, "outcome_type": outcome.outcome_type}
            )
            db.add(cost_entry)
            db.commit()
            logger.info(f"Auto-recorded outcome cost 0.0 {outcome.currency} for agent: {agent.name}")
    return outcome
