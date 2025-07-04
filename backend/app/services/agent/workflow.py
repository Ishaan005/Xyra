"""
Workflow operations for agents.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.agent import AgentCost as AgentCostModel
from app.services.billing_model.calculation import calculate_cost
from .core import get_agent

logger = logging.getLogger(__name__)


def record_agent_workflow(db: Session, agent_id: int, workflow_type: str, workflow_metadata: Optional[Dict[str, Any]] = None) -> AgentCostModel:
    """
    Record a workflow execution for an agent and auto-calculate cost
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    # Get billing model
    bm = agent.billing_model
    if not bm or bm.model_type != "workflow":
        raise ValueError(f"Agent {agent_id} does not have a workflow billing model")
    
    # Find matching workflow type config
    workflow_configs = bm.workflow_types or []
    matching_config = None
    for cfg in workflow_configs:
        if cfg.workflow_type == workflow_type:
            matching_config = cfg
            break
    
    if not matching_config:
        raise ValueError(f"No workflow configuration found for type: {workflow_type}")
    
    # Calculate cost based on workflow config
    usage_data = {"workflows": {workflow_type: 1}}
    cost_amt = calculate_cost(bm, usage_data)
    
    # Create cost entry for workflow
    cost_entry = AgentCostModel(
        agent_id=agent_id,
        cost_type="workflow",
        amount=cost_amt,
        currency=bm.workflow_config.currency if bm.workflow_config else "USD",
        timestamp=datetime.now(timezone.utc),
        details={
            "workflow_type": workflow_type,
            "workflow_name": matching_config.workflow_name,
            "complexity_level": matching_config.complexity_level,
            "estimated_duration_minutes": matching_config.estimated_duration_minutes,
            "business_value_category": matching_config.business_value_category,
            "metadata": workflow_metadata or {}
        }
    )
    
    db.add(cost_entry)
    db.commit()
    db.refresh(cost_entry)
    
    logger.info(f"Recorded workflow execution {workflow_type} cost {cost_amt} for agent: {agent.name}")
    return cost_entry


def record_bulk_workflows(db: Session, agent_id: int, workflow_executions: Dict[str, int], commitment_exceeded: bool = False) -> List[AgentCostModel]:
    """
    Record multiple workflow executions at once for an agent
    
    Args:
        agent_id: ID of the agent
        workflow_executions: Dictionary mapping workflow types to execution counts
        commitment_exceeded: Whether these executions exceed the commitment tier
    
    Returns:
        List of created cost entries
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    # Get billing model
    bm = agent.billing_model
    if not bm or bm.model_type != "workflow":
        raise ValueError(f"Agent {agent_id} does not have a workflow billing model")
    
    # Calculate cost for all workflows
    usage_data = {
        "workflows": workflow_executions,
        "commitment_exceeded": commitment_exceeded
    }
    total_cost = calculate_cost(bm, usage_data)
    
    # Create individual cost entries for each workflow type
    cost_entries = []
    total_workflows = sum(workflow_executions.values())
    
    for workflow_type, count in workflow_executions.items():
        if count <= 0:
            continue
            
        # Find matching workflow config
        matching_config = None
        for cfg in bm.workflow_types:
            if cfg.workflow_type == workflow_type:
                matching_config = cfg
                break
        
        if not matching_config:
            logger.warning(f"No workflow configuration found for type: {workflow_type}")
            continue
        
        # Calculate proportional cost for this workflow type
        proportional_cost = (count / total_workflows) * total_cost if total_workflows > 0 else 0
        
        cost_entry = AgentCostModel(
            agent_id=agent_id,
            cost_type="workflow",
            amount=proportional_cost,
            currency=bm.workflow_config.currency if bm.workflow_config else "USD",
            timestamp=datetime.now(timezone.utc),
            details={
                "workflow_type": workflow_type,
                "workflow_name": matching_config.workflow_name,
                "workflow_count": count,
                "total_workflows_in_batch": total_workflows,
                "commitment_exceeded": commitment_exceeded,
                "complexity_level": matching_config.complexity_level,
                "business_value_category": matching_config.business_value_category,
                "batch_total_cost": total_cost
            }
        )
        
        cost_entries.append(cost_entry)
        db.add(cost_entry)
    
    db.commit()
    logger.info(f"Recorded {len(cost_entries)} workflow cost entries totaling {total_cost} for agent: {agent.name}")
    
    return cost_entries
