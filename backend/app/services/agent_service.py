from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.agent import Agent, AgentActivity, AgentCost, AgentOutcome
from app.models.organization import Organization
from app.schemas.agent import (
    AgentCreate, AgentUpdate, 
    AgentActivityCreate, AgentCostCreate, AgentOutcomeCreate,
    AgentActivity  # Added missing import for AgentActivity schema
)

# Configure logging
logger = logging.getLogger(__name__)


def get_agent(db: Session, agent_id: int) -> Optional[Agent]:
    """
    Get agent by ID
    """
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agent_by_external_id(db: Session, external_id: str) -> Optional[Agent]:
    """
    Get agent by external ID
    """
    return db.query(Agent).filter(Agent.external_id == external_id).first()


def get_agents_by_organization(
    db: Session, org_id: int, skip: int = 0, limit: int = 100, active_only: bool = False
) -> List[Agent]:
    """
    Get all agents for an organization with pagination
    """
    query = db.query(Agent).filter(Agent.organization_id == org_id)
    
    if active_only:
        query = query.filter(Agent.is_active == True)
    
    return query.offset(skip).limit(limit).all()


def create_agent(db: Session, agent_in: AgentCreate) -> Agent:
    """
    Create a new agent for an organization
    """
    # Check if organization exists
    organization = db.query(Organization).filter(
        Organization.id == agent_in.organization_id
    ).first()
    
    if not organization:
        raise ValueError(f"Organization with ID {agent_in.organization_id} not found")
    
    # Create agent
    agent = Agent(
        name=agent_in.name,
        description=agent_in.description,
        organization_id=agent_in.organization_id,
        billing_model_id=agent_in.billing_model_id,
        config=agent_in.config,
        is_active=agent_in.is_active,
        external_id=agent_in.external_id,
        last_active=datetime.utcnow(),
    )
    
    # Add agent to database
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    logger.info(f"Created new agent: {agent.name} for organization {organization.name}")
    return agent


def update_agent(db: Session, agent_id: int, agent_in: AgentUpdate) -> Optional[Agent]:
    """
    Update an agent
    """
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        logger.warning(f"Agent update failed: Agent not found with ID {agent_id}")
        return None
    
    # Update agent properties - Updated to use model_dump instead of dict for Pydantic v2
    update_data = agent_in.model_dump(exclude_unset=True)
    
    # Update agent attributes
    for field, value in update_data.items():
        if hasattr(agent, field):
            setattr(agent, field, value)
    
    # Update last active timestamp if the agent is active
    if agent.is_active:
        agent.last_active = datetime.utcnow()
    
    # Commit changes to database
    db.commit()
    db.refresh(agent)
    
    logger.info(f"Updated agent: {agent.name}")
    return agent


def delete_agent(db: Session, agent_id: int) -> Optional[Agent]:
    """
    Delete an agent
    """
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        logger.warning(f"Agent deletion failed: Agent not found with ID {agent_id}")
        return None
    
    # Delete agent from database
    db.delete(agent)
    db.commit()
    
    logger.info(f"Deleted agent: {agent.name}")
    return agent


def record_agent_activity(db: Session, activity_in: AgentActivityCreate) -> AgentActivity:
    """
    Record an activity for an agent
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=activity_in.agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {activity_in.agent_id} not found")
    
    # Create activity
    activity = AgentActivity(
        agent_id=activity_in.agent_id,
        activity_type=activity_in.activity_type,
        timestamp=datetime.utcnow(),
        activity_metadata=activity_in.activity_metadata,
    )
    
    # Add activity to database
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    # Update agent's last active timestamp
    agent.last_active = datetime.utcnow()
    db.commit()
    
    logger.info(f"Recorded activity {activity.activity_type} for agent: {agent.name}")
    return activity


def record_agent_cost(db: Session, cost_in: AgentCostCreate) -> AgentCost:
    """
    Record a cost for an agent
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=cost_in.agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {cost_in.agent_id} not found")
    
    # Create cost
    cost = AgentCost(
        agent_id=cost_in.agent_id,
        cost_type=cost_in.cost_type,
        amount=cost_in.amount,
        currency=cost_in.currency,
        timestamp=datetime.utcnow(),
        details=cost_in.details,
    )
    
    # Add cost to database
    db.add(cost)
    db.commit()
    db.refresh(cost)
    
    logger.info(f"Recorded cost {cost.amount} {cost.currency} for agent: {agent.name}")
    return cost


def record_agent_outcome(db: Session, outcome_in: AgentOutcomeCreate) -> AgentOutcome:
    """
    Record an outcome for an agent
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=outcome_in.agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {outcome_in.agent_id} not found")
    
    # Create outcome
    outcome = AgentOutcome(
        agent_id=outcome_in.agent_id,
        outcome_type=outcome_in.outcome_type,
        value=outcome_in.value,
        currency=outcome_in.currency,
        timestamp=datetime.utcnow(),
        details=outcome_in.details,
        verified=outcome_in.verified,
    )
    
    # Add outcome to database
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    
    logger.info(f"Recorded outcome {outcome.value} {outcome.currency} for agent: {agent.name}")
    return outcome


def get_agent_stats(db: Session, agent_id: int) -> Dict[str, Any]:
    """
    Get statistics for an agent including activity count, costs, and outcomes
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    # Count activities
    activity_count = db.query(func.count(AgentActivity.id)).filter(
        AgentActivity.agent_id == agent_id
    ).scalar() or 0
    
    # Sum costs
    total_cost = db.query(func.sum(AgentCost.amount)).filter(
        AgentCost.agent_id == agent_id
    ).scalar() or 0.0
    
    # Sum outcomes
    total_outcomes_value = db.query(func.sum(AgentOutcome.value)).filter(
        AgentOutcome.agent_id == agent_id
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