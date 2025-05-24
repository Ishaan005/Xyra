from typing import List, Optional, Dict, Any
import logging
import stripe
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models.organization import Organization
from app.models.agent import Agent, AgentCost, AgentOutcome
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Stripe client
stripe.api_key = settings.STRIPE_API_KEY


def get_organization(db: Session, org_id: int) -> Optional[Organization]:
    """
    Get organization by ID
    """
    return db.query(Organization).filter(Organization.id == org_id).first()


def get_organization_by_name(db: Session, name: str) -> Optional[Organization]:
    """
    Get organization by name
    """
    return db.query(Organization).filter(Organization.name == name).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[Organization]:
    """
    Get multiple organizations with pagination
    """
    return db.query(Organization).offset(skip).limit(limit).all()


def create_organization(db: Session, org_in: OrganizationCreate) -> Organization:
    """
    Create a new organization with optional Stripe customer
    """
    # Check if organization already exists
    db_org = get_organization_by_name(db, name=org_in.name)
    if db_org:
        raise ValueError(f"Organization with name {org_in.name} already exists")
    
    # Create Stripe customer if Stripe is configured
    stripe_customer_id = None
    if settings.STRIPE_API_KEY:
        try:
            stripe_customer = stripe.Customer.create(
                name=org_in.name,
                description=org_in.description or "",
                metadata={"source": "business_engine"}
            )
            stripe_customer_id = stripe_customer.id
            logger.info(f"Created Stripe customer for organization {org_in.name}: {stripe_customer_id}")
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
    
    # Create organization
    org = Organization(
        name=org_in.name,
        description=org_in.description,
        stripe_customer_id=stripe_customer_id,
    )
    
    # Add organization to database
    db.add(org)
    db.commit()
    db.refresh(org)
    
    logger.info(f"Created new organization: {org.name}")
    return org


def update_organization(db: Session, org_id: int, org_in: OrganizationUpdate) -> Optional[Organization]:
    """
    Update an organization
    """
    org = get_organization(db, org_id=org_id)
    if not org:
        logger.warning(f"Organization update failed: Organization not found with ID {org_id}")
        return None
    
    # Update organization properties - Using model_dump instead of dict for Pydantic v2
    update_data = org_in.model_dump(exclude_unset=True)
    
    # Update organization attributes
    for field, value in update_data.items():
        if hasattr(org, field):
            setattr(org, field, value)
    
    # Update Stripe customer if needed and Stripe is configured
    if settings.STRIPE_API_KEY and org.stripe_customer_id is not None and update_data:
        try:
            stripe_update_data = {}
            if "name" in update_data:
                stripe_update_data["name"] = update_data["name"]
            if "description" in update_data:
                stripe_update_data["description"] = update_data["description"]
                
            if stripe_update_data:
                stripe.Customer.modify(str(org.stripe_customer_id), **stripe_update_data)
                logger.info(f"Updated Stripe customer for organization {org.name}: {org.stripe_customer_id}")
        except Exception as e:
            logger.error(f"Failed to update Stripe customer: {str(e)}")
    
    # Commit changes to database
    db.commit()
    db.refresh(org)
    
    logger.info(f"Updated organization: {org.name}")
    return org


def delete_organization(db: Session, org_id: int) -> Optional[Organization]:
    """
    Delete an organization and optionally its Stripe customer
    """
    org = get_organization(db, org_id=org_id)
    if not org:
        logger.warning(f"Organization deletion failed: Organization not found with ID {org_id}")
        return None
    
    # Delete Stripe customer if it exists and Stripe is configured
    if settings.STRIPE_API_KEY and org.stripe_customer_id is not None:
        try:
            customer = stripe.Customer.retrieve(str(org.stripe_customer_id))
            customer.delete()
            logger.info(f"Deleted Stripe customer for organization {org.name}: {org.stripe_customer_id}")
        except Exception as e:
            logger.error(f"Failed to delete Stripe customer: {str(e)}")
    
    # Delete organization from database
    db.delete(org)
    db.commit()
    
    logger.info(f"Deleted organization: {org.name}")
    return org


def get_organization_stats(db: Session, org_id: int) -> Dict[str, Any]:
    """
    Get organization statistics including agent counts, costs, and revenues
    """
    org = get_organization(db, org_id=org_id)
    if not org:
        logger.warning(f"Stats retrieval failed: Organization not found with ID {org_id}")
        return {}
    
    # Get agent counts
    agent_count = db.query(func.count(Agent.id)).filter(Agent.organization_id == org_id).scalar() or 0
    active_agent_count = db.query(func.count(Agent.id)).filter(
        Agent.organization_id == org_id, Agent.is_active == True
    ).scalar() or 0
    
    # Get monthly cost (sum of all agent costs in the last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    monthly_cost = db.query(func.sum(AgentCost.amount)).filter(
        AgentCost.agent_id.in_(
            db.query(Agent.id).filter(Agent.organization_id == org_id)
        ),
        AgentCost.created_at >= thirty_days_ago
    ).scalar() or 0.0
    
    # Get monthly revenue (sum of all agent outcomes in the last 30 days)
    monthly_revenue = db.query(func.sum(AgentOutcome.value)).filter(
        AgentOutcome.agent_id.in_(
            db.query(Agent.id).filter(Agent.organization_id == org_id)
        ),
        AgentOutcome.created_at >= thirty_days_ago
    ).scalar() or 0.0
    
    return {
        "agent_count": agent_count,
        "active_agent_count": active_agent_count,
        "monthly_cost": monthly_cost,
        "monthly_revenue": monthly_revenue
    }