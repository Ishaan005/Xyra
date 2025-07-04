"""
Core agent operations - CRUD operations for agents.
"""

from typing import List, Optional
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.organization import Organization
from app.schemas.agent import AgentCreate, AgentUpdate

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
        last_active=datetime.now(timezone.utc),
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
    if agent.is_active is True:
        setattr(agent, 'last_active', datetime.now(timezone.utc))
    
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

    # Manually delete related records to avoid FK constraint violations
    from app.models.agent import AgentActivity, AgentCost, AgentOutcome
    db.query(AgentActivity).filter(AgentActivity.agent_id == agent_id).delete(synchronize_session=False)
    db.query(AgentCost).filter(AgentCost.agent_id == agent_id).delete(synchronize_session=False)
    db.query(AgentOutcome).filter(AgentOutcome.agent_id == agent_id).delete(synchronize_session=False)
    # Delete agent
    db.delete(agent)
    db.commit()
    logger.info(f"Deleted agent and related records: {agent.name}")
    return agent
