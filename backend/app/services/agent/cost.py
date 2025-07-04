"""
Cost operations for agents.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.agent import AgentCost as AgentCostModel
from app.schemas.agent import AgentCostCreate
from app.services.billing_model.calculation import calculate_cost
from .core import get_agent

logger = logging.getLogger(__name__)


def record_agent_cost(db: Session, cost_in: AgentCostCreate) -> AgentCostModel:
    """
    Record a cost for an agent
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=cost_in.agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {cost_in.agent_id} not found")
    
    # Create cost, calculating via billing model config if available
    bm = agent.billing_model
    amount = cost_in.amount  # Default to provided amount
    
    if bm and cost_in.details:
        # Calculate based on billing model config if possible
        try:
            # For activity-based costs, use activity type information
            if cost_in.cost_type == "activity" and "activity_type" in cost_in.details:
                activity_type = cost_in.details["activity_type"]
                units = cost_in.details.get("units", 1)
                usage_data = {"units": units, "activity_type": activity_type}
                computed = calculate_cost(bm, usage_data)
                amount = computed
            # For outcome-based costs, use outcome value
            elif cost_in.cost_type == "outcome" and "outcome_value" in cost_in.details:
                outcome_value = cost_in.details["outcome_value"]
                outcome_type = cost_in.details.get("outcome_type")
                usage_data = {"outcome_value": outcome_value}
                if outcome_type:
                    usage_data["outcome_type"] = outcome_type
                computed = calculate_cost(bm, usage_data)
                amount = computed
            # For workflow-based costs, use workflow type information
            elif cost_in.cost_type == "workflow" and "workflow_type" in cost_in.details:
                workflow_type = cost_in.details["workflow_type"]
                workflow_count = cost_in.details.get("workflow_count", 1)
                usage_data = {"workflows": {workflow_type: workflow_count}}
                computed = calculate_cost(bm, usage_data)
                amount = computed
            # For agent-based costs, use agent count
            elif cost_in.cost_type == "agent" and bm.model_type == "agent":
                agents = cost_in.details.get("agents", 1)
                include_setup = cost_in.details.get("include_setup_fee", False)
                usage_data = {"agents": agents, "include_setup_fee": include_setup}
                computed = calculate_cost(bm, usage_data)
                amount = computed
            else:
                # Generic calculation with provided details
                computed = calculate_cost(bm, cost_in.details)
                amount = computed
        except Exception as e:
            logger.warning(f"Failed to calculate cost via billing model: {e}")
            # Fall back to provided amount
            amount = cost_in.amount
    
    cost = AgentCostModel(
        agent_id=cost_in.agent_id,
        cost_type=cost_in.cost_type,
        amount=amount,
        currency=cost_in.currency,
        timestamp=datetime.now(timezone.utc),
        details=cost_in.details,
    )
    
    # Add cost to database
    db.add(cost)
    db.commit()
    db.refresh(cost)
    
    logger.info(f"Recorded cost {cost.amount} {cost.currency} for agent: {agent.name}")
    return cost
