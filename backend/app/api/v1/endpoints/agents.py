from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import agent_service, organization_service

router = APIRouter()


@router.get("", response_model=List[schemas.Agent])
def read_agents(
    org_id: int = Query(..., description="Organization ID to filter agents"),
    active_only: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve agents for an organization.
    
    Users can only access agents for their own organization unless they are superusers.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access agents for this organization",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Get agents for the organization
    agents = agent_service.get_agents_by_organization(
        db, org_id=org_id, skip=skip, limit=limit, active_only=active_only or False
    )
    
    return agents


@router.post("", response_model=schemas.Agent)
def create_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_in: schemas.AgentCreate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new agent for an organization.
    
    Users can only create agents for their own organization unless they are superusers.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent_in.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create agents for this organization",
        )
    
    # Create agent
    try:
        agent = agent_service.create_agent(db, agent_in=agent_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return agent


@router.get("/{agent_id}", response_model=schemas.Agent)
def read_agent(
    agent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user_flexible),
) -> Any:
    """
    Get a specific agent by ID.
    
    Users can only access agents for their own organization unless they are superusers.
    """
    # Get agent
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this agent",
        )
    
    return agent


@router.get("/external/{external_id}", response_model=schemas.Agent)
def read_agent_by_external_id(
    external_id: str,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific agent by external ID.
    
    Users can only access agents for their own organization unless they are superusers.
    """
    # Get agent
    agent = agent_service.get_agent_by_external_id(db, external_id=external_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this agent",
        )
    
    return agent


@router.put("/{agent_id}", response_model=schemas.Agent)
def update_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    agent_in: schemas.AgentUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an agent.
    
    Users can only update agents for their own organization unless they are superusers.
    """
    # Get agent
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this agent",
        )
    
    # Update agent
    try:
        updated_agent = agent_service.update_agent(db, agent_id=agent_id, agent_in=agent_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return updated_agent


@router.delete("/{agent_id}", response_model=schemas.Agent)
def delete_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an agent.
    
    Users can only delete agents for their own organization unless they are superusers.
    """
    # Get agent
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this agent",
        )
    
    # Delete agent
    agent = agent_service.delete_agent(db, agent_id=agent_id)
    return agent


@router.post("/{agent_id}/activities", response_model=schemas.AgentActivity)
def record_activity(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    activity_in: schemas.AgentActivityCreate,
    current_user: schemas.User = Depends(deps.get_current_user_flexible),
) -> Any:
    """
    Record activity for an agent.
    
    Users can only record activities for agents in their own organization unless they are superusers.
    """
    # Ensure agent_id in path matches the one in the request body
    if agent_id != activity_in.agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent ID in path must match the one in request body",
        )
    
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to record activities for this agent",
        )
    
    # Record activity
    try:
        activity = agent_service.record_agent_activity(db, activity_in=activity_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return activity


@router.post("/{agent_id}/costs", response_model=schemas.AgentCost)
def record_cost(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    cost_in: schemas.AgentCostCreate,
    current_user: schemas.User = Depends(deps.get_current_user_flexible),
) -> Any:
    """
    Record cost for an agent.
    
    Users can only record costs for agents in their own organization unless they are superusers.
    """
    # Ensure agent_id in path matches the one in the request body
    if agent_id != cost_in.agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent ID in path must match the one in request body",
        )
    
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to record costs for this agent",
        )
    
    # Record cost
    try:
        cost = agent_service.record_agent_cost(db, cost_in=cost_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return cost


@router.post("/{agent_id}/outcomes", response_model=schemas.AgentOutcome)
def record_outcome(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    outcome_in: schemas.AgentOutcomeCreate,
    current_user: schemas.User = Depends(deps.get_current_user_flexible),
) -> Any:
    """
    Record outcome for an agent.
    
    Users can only record outcomes for agents in their own organization unless they are superusers.
    """
    # Ensure agent_id in path matches the one in the request body
    if agent_id != outcome_in.agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent ID in path must match the one in request body",
        )
    
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to record outcomes for this agent",
        )
    
    # Record outcome
    try:
        outcome = agent_service.record_agent_outcome(db, outcome_in=outcome_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return outcome


@router.get("/{agent_id}/stats", response_model=schemas.AgentWithStats)
def get_agent_stats(
    agent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get statistics for an agent including activity count, costs, and outcomes.
    
    Users can only access stats for agents in their own organization unless they are superusers.
    """
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access stats for this agent",
        )
    
    # Get agent stats
    try:
        stats = agent_service.get_agent_stats(db, agent_id=agent_id)
        
        # Combine agent data with stats
        agent_data = {
            **agent.__dict__,
            **stats
        }
        
        return agent_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{agent_id}/billing-config", response_model=dict)
def get_agent_billing_config(
    agent_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user_flexible),
) -> Any:
    """
    Get billing configuration for an agent.
    
    Users can only access billing config for agents in their own organization unless they are superusers.
    """
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access billing config for this agent",
        )
    
    # Get agent billing config
    config = agent_service.get_agent_billing_config(db, agent_id=agent_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No billing configuration found for this agent",
        )
    
    return config


@router.get("/{agent_id}/billing-summary", response_model=dict)
def get_agent_billing_summary(
    agent_id: int,
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed billing summary for an agent.
    
    Users can only access billing summary for agents in their own organization unless they are superusers.
    """
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access billing summary for this agent",
        )
    
    # Parse dates if provided
    from datetime import datetime
    parsed_start_date = None
    parsed_end_date = None
    
    if start_date:
        try:
            parsed_start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (e.g., 2023-01-01T00:00:00Z)",
            )
    
    if end_date:
        try:
            parsed_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (e.g., 2023-01-01T00:00:00Z)",
            )
    
    # Get agent billing summary
    try:
        summary = agent_service.get_agent_billing_summary(
            db, agent_id=agent_id, start_date=parsed_start_date, end_date=parsed_end_date
        )
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{agent_id}/workflows/bulk", response_model=List[schemas.AgentCost])
def record_bulk_workflows(
    agent_id: int,
    workflow_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Record multiple workflow executions for an agent.
    
    Expected request body:
    {
        "workflow_executions": {
            "lead_research": 5,
            "email_personalization": 10
        },
        "commitment_exceeded": false
    }
    """
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to record workflows for this agent",
        )
    
    # Validate request data
    workflow_executions = workflow_data.get("workflow_executions", {})
    commitment_exceeded = workflow_data.get("commitment_exceeded", False)
    
    if not workflow_executions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workflow_executions must be provided and non-empty",
        )
    
    # Record bulk workflows
    try:
        cost_entries = agent_service.record_bulk_workflows(
            db, agent_id=agent_id, workflow_executions=workflow_executions, commitment_exceeded=commitment_exceeded
        )
        return cost_entries
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{agent_id}/workflows/validate", response_model=dict)
def validate_workflow_billing_data(
    agent_id: int,
    workflow_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Validate workflow execution data against agent's billing model.
    
    Expected request body:
    {
        "workflow_executions": {
            "lead_research": 5,
            "email_personalization": 10
        }
    }
    """
    # Get agent to check permissions
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != agent.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to validate workflows for this agent",
        )
    
    # Validate request data
    workflow_executions = workflow_data.get("workflow_executions", {})
    
    if not workflow_executions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workflow_executions must be provided and non-empty",
        )
    
    # Validate workflow billing data
    validation_result = agent_service.validate_workflow_billing_data(
        db, agent_id=agent_id, workflow_executions=workflow_executions
    )
    
    return validation_result