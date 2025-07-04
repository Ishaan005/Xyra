"""
Statistics operations for agents.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.agent import AgentActivity as AgentActivityModel, AgentCost as AgentCostModel, AgentOutcome as AgentOutcomeModel
from .core import get_agent

logger = logging.getLogger(__name__)


def get_agent_stats(db: Session, agent_id: int) -> Dict[str, Any]:
    """
    Get statistics for an agent including activity count, costs, and outcomes
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    # Count activities
    activity_count = db.query(func.count(AgentActivityModel.id)).filter(
        AgentActivityModel.agent_id == agent_id
    ).scalar() or 0
    
    # Sum costs
    total_cost = db.query(func.sum(AgentCostModel.amount)).filter(
        AgentCostModel.agent_id == agent_id
    ).scalar() or 0.0
    
    # Sum outcomes
    total_outcomes_value = db.query(func.sum(AgentOutcomeModel.value)).filter(
        AgentOutcomeModel.agent_id == agent_id
    ).scalar() or 0.0
    
    # Calculate margin
    margin = 0.0
    if total_outcomes_value > 0:
        margin = (total_outcomes_value - total_cost) / total_outcomes_value
    
    return {
        "activity_count": activity_count,
        "total_cost": total_cost,
        "total_outcomes_value": total_outcomes_value,
        "margin": margin
    }


def get_agent_billing_summary(db: Session, agent_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get detailed billing summary for an agent including breakdown by cost type
    
    Args:
        agent_id: ID of the agent
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
    
    Returns:
        Dictionary with detailed billing information
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    # Base query for costs
    cost_query = db.query(AgentCostModel).filter(AgentCostModel.agent_id == agent_id)
    
    # Apply date filters if provided
    if start_date:
        cost_query = cost_query.filter(AgentCostModel.timestamp >= start_date)
    if end_date:
        cost_query = cost_query.filter(AgentCostModel.timestamp <= end_date)
    
    # Get all costs
    costs = cost_query.all()
    
    # Initialize summary
    summary = {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "billing_model": {
            "id": agent.billing_model.id if agent.billing_model else None,
            "name": agent.billing_model.name if agent.billing_model else None,
            "type": agent.billing_model.model_type if agent.billing_model else None
        },
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "total_cost": 0.0,
        "cost_by_type": {},
        "cost_breakdown": [],
        "activity_stats": {},
        "workflow_stats": {},
        "outcome_stats": {}
    }
    
    # Process costs
    for cost in costs:
        cost_type = str(cost.cost_type)
        amount = cost.amount
        details = cost.details
        
        # Add to total
        summary["total_cost"] += amount
        
        # Add to cost by type
        if cost_type not in summary["cost_by_type"]:
            summary["cost_by_type"][cost_type] = {"total": 0.0, "count": 0}
        summary["cost_by_type"][cost_type]["total"] += amount
        summary["cost_by_type"][cost_type]["count"] += 1
        
        # Add to breakdown
        summary["cost_breakdown"].append({
            "id": cost.id,
            "type": cost_type,
            "amount": amount,
            "currency": cost.currency,
            "timestamp": cost.timestamp.isoformat(),
            "details": details
        })
        
        # Collect type-specific stats
        if cost_type == "activity" and details is not None:
            activity_type = details.get("activity_type")
            if activity_type:
                if activity_type not in summary["activity_stats"]:
                    summary["activity_stats"][activity_type] = {"total_cost": 0.0, "count": 0}
                summary["activity_stats"][activity_type]["total_cost"] += amount
                summary["activity_stats"][activity_type]["count"] += 1
        
        elif cost_type == "workflow" and details is not None:
            workflow_type = details.get("workflow_type")
            if workflow_type:
                if workflow_type not in summary["workflow_stats"]:
                    summary["workflow_stats"][workflow_type] = {"total_cost": 0.0, "count": 0}
                summary["workflow_stats"][workflow_type]["total_cost"] += amount
                summary["workflow_stats"][workflow_type]["count"] += details.get("workflow_count", 1)
        
        elif cost_type == "outcome" and details is not None:
            outcome_type = details.get("outcome_type")
            if outcome_type:
                if outcome_type not in summary["outcome_stats"]:
                    summary["outcome_stats"][outcome_type] = {"total_cost": 0.0, "count": 0}
                summary["outcome_stats"][outcome_type]["total_cost"] += amount
                summary["outcome_stats"][outcome_type]["count"] += 1
    
    return summary
