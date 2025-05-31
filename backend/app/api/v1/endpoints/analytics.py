from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import schemas
from app.api import deps
from app.api.data_processing_deps import get_data_processing_pipeline, get_enrichment_service
from app.models.agent import Agent, AgentActivity, AgentCost, AgentOutcome
from app.models.organization import Organization
from app.services import agent_service, organization_service
from app.services.data_processing_pipeline import DataProcessingPipeline
from app.services.data_enrichment import DataEnrichmentService, EnrichmentRule, EnrichmentType, EnrichmentPriority

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/organization/{org_id}/summary", response_model=Dict[str, Any])
def get_organization_summary(
    org_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for analytics (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics (defaults to now)"),
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get summary analytics for an organization.
    
    Returns aggregate metrics for all agents in the organization within the specified date range.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics for this organization",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
    if not end_date:
        end_date = datetime.now(timezone.utc)
    
    # Get all agents for this organization
    agents = agent_service.get_agents_by_organization(db, org_id=org_id)
    agent_ids = [agent.id for agent in agents]
    
    if not agent_ids:
        return {
            "organization_id": org_id,
            "organization_name": organization.name,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "metrics": {
                "activity_count": 0,
                "total_cost": 0.0,
                "total_revenue": 0.0,
                "margin": 0.0
            },
            "agents": {
                "total": 0,
                "active": 0
            }
        }
    
    # Query agent activities in date range
    activity_count = db.query(func.count(AgentActivity.id)).filter(
        AgentActivity.agent_id.in_(agent_ids),
        AgentActivity.timestamp >= start_date,
        AgentActivity.timestamp <= end_date
    ).scalar() or 0
    
    # Query agent costs in date range
    total_cost = db.query(func.sum(AgentCost.amount)).filter(
        AgentCost.agent_id.in_(agent_ids),
        AgentCost.timestamp >= start_date,
        AgentCost.timestamp <= end_date
    ).scalar() or 0.0
    
    # Query agent outcomes in date range
    total_revenue = db.query(func.sum(AgentOutcome.value)).filter(
        AgentOutcome.agent_id.in_(agent_ids),
        AgentOutcome.timestamp >= start_date,
        AgentOutcome.timestamp <= end_date
    ).scalar() or 0.0
    
    # Calculate margin
    margin = 0.0
    if total_revenue > 0:
        margin = (total_revenue - total_cost) / total_revenue
    
    # Count active agents
    active_agents = db.query(func.count(Agent.id)).filter(
        Agent.organization_id == org_id,
        Agent.is_active == True
    ).scalar() or 0
    
    # Build response
    return {
        "organization_id": org_id,
        "organization_name": organization.name,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "metrics": {
            "activity_count": activity_count,
            "total_cost": total_cost,
            "total_revenue": total_revenue,
            "margin": margin
        },
        "agents": {
            "total": len(agents),
            "active": active_agents
        }
    }


@router.get("/organization/{org_id}/top-agents", response_model=List[Dict[str, Any]])
def get_top_agents(
    org_id: int,
    metric: str = Query("margin", description="Metric to sort by: 'margin', 'revenue', 'cost', 'activity'"),
    limit: int = Query(5, description="Number of agents to return"),
    start_date: Optional[datetime] = Query(None, description="Start date for analytics (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics (defaults to now)"),
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get top performing agents for an organization by specified metric.
    
    Returns agents sorted by the specified metric within the given date range.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics for this organization",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
    if not end_date:
        end_date = datetime.now(timezone.utc)
    
    # Get all agents for this organization
    agents = agent_service.get_agents_by_organization(db, org_id=org_id)
    
    # For each agent, calculate the requested metric
    agent_metrics = []
    for agent in agents:
        # Get agent stats
        try:
            # Count activities
            activity_count = db.query(func.count(AgentActivity.id)).filter(
                AgentActivity.agent_id == agent.id,
                AgentActivity.timestamp >= start_date,
                AgentActivity.timestamp <= end_date
            ).scalar() or 0
            
            # Sum costs
            total_cost = db.query(func.sum(AgentCost.amount)).filter(
                AgentCost.agent_id == agent.id,
                AgentCost.timestamp >= start_date,
                AgentCost.timestamp <= end_date
            ).scalar() or 0.0
            
            # Sum revenues (outcomes)
            total_revenue = db.query(func.sum(AgentOutcome.value)).filter(
                AgentOutcome.agent_id == agent.id,
                AgentOutcome.timestamp >= start_date,
                AgentOutcome.timestamp <= end_date
            ).scalar() or 0.0
            
            # Calculate margin
            margin = 0.0
            if total_revenue > 0:
                margin = (total_revenue - total_cost) / total_revenue
            
            # Add agent metrics to list
            agent_metrics.append({
                "agent_id": agent.id,
                "name": agent.name,
                "is_active": agent.is_active,
                "metrics": {
                    "activity_count": activity_count,
                    "total_cost": total_cost,
                    "total_revenue": total_revenue,
                    "margin": margin
                }
            })
        except Exception as e:
            # Skip agents with errors
            continue
    
    # Sort agents by the specified metric
    if metric == "margin":
        agent_metrics.sort(key=lambda x: x["metrics"]["margin"], reverse=True)
    elif metric == "revenue":
        agent_metrics.sort(key=lambda x: x["metrics"]["total_revenue"], reverse=True)
    elif metric == "cost":
        agent_metrics.sort(key=lambda x: x["metrics"]["total_cost"], reverse=True)
    elif metric == "activity":
        agent_metrics.sort(key=lambda x: x["metrics"]["activity_count"], reverse=True)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metric: {metric}. Must be one of: margin, revenue, cost, activity",
        )
    
    # Return top N agents
    return agent_metrics[:limit]


@router.get("/agent/{agent_id}/daily-metrics", response_model=List[Dict[str, Any]])
def get_agent_daily_metrics(
    agent_id: int,
    days: int = Query(30, description="Number of days to include"),
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get daily metrics for a specific agent over the past N days.
    
    Returns a time series of daily activity, cost, and revenue data.
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
            detail="Not enough permissions to access metrics for this agent",
        )
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Generate list of days
    daily_metrics = []
    current_date = start_date.date()
    end_date_only = end_date.date()
    
    while current_date <= end_date_only:
        day_start = datetime.combine(current_date, datetime.min.time())
        day_end = datetime.combine(current_date, datetime.max.time())
        
        # Count activities for this day
        activity_count = db.query(func.count(AgentActivity.id)).filter(
            AgentActivity.agent_id == agent_id,
            AgentActivity.timestamp >= day_start,
            AgentActivity.timestamp <= day_end
        ).scalar() or 0
        
        # Sum costs for this day
        day_cost = db.query(func.sum(AgentCost.amount)).filter(
            AgentCost.agent_id == agent_id,
            AgentCost.timestamp >= day_start,
            AgentCost.timestamp <= day_end
        ).scalar() or 0.0
        
        # Sum revenues for this day
        day_revenue = db.query(func.sum(AgentOutcome.value)).filter(
            AgentOutcome.agent_id == agent_id,
            AgentOutcome.timestamp >= day_start,
            AgentOutcome.timestamp <= day_end
        ).scalar() or 0.0
        
        # Calculate margin
        margin = 0.0
        if day_revenue > 0:
            margin = (day_revenue - day_cost) / day_revenue
        
        # Add day to metrics
        daily_metrics.append({
            "date": current_date.isoformat(),
            "activity_count": activity_count,
            "cost": day_cost,
            "revenue": day_revenue,
            "margin": margin
        })
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return daily_metrics


@router.get("/organization/{org_id}/activity-breakdown", response_model=Dict[str, Any])
def get_activity_breakdown(
    org_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description="End date (defaults to now)"),
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get breakdown of agent activities by type for an organization.
    
    Returns counts of different activity types within the specified date range.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics for this organization",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
    if not end_date:
        end_date = datetime.now(timezone.utc)
    
    # Get all agents for this organization
    agents = agent_service.get_agents_by_organization(db, org_id=org_id)
    agent_ids = [agent.id for agent in agents]
    
    if not agent_ids:
        return {
            "organization_id": org_id,
            "organization_name": organization.name,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_activities": 0,
            "activity_types": {}
        }
    
    # Query all activities in date range
    activities = db.query(
        AgentActivity.activity_type, 
        func.count(AgentActivity.id).label("count")
    ).filter(
        AgentActivity.agent_id.in_(agent_ids),
        AgentActivity.timestamp >= start_date,
        AgentActivity.timestamp <= end_date
    ).group_by(AgentActivity.activity_type).all()
    
    # Calculate total activities
    total_activities = sum(count for _, count in activities)
    
    # Build activity type breakdown
    activity_types = {activity_type: count for activity_type, count in activities}
    
    # Add percentage for each type
    activity_types_with_percent = {}
    for activity_type, count in activity_types.items():
        percent = (count / total_activities * 100) if total_activities > 0 else 0
        activity_types_with_percent[activity_type] = {
            "count": count,
            "percentage": round(percent, 2)
        }
    
    return {
        "organization_id": org_id,
        "organization_name": organization.name,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "total_activities": total_activities,
        "activity_types": activity_types_with_percent
    }


@router.post("/organization/{org_id}/enhanced-insights", response_model=Dict[str, Any])
async def get_enhanced_analytics_insights(
    org_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for analytics (defaults to 30 days ago)"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics (defaults to now)"),
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
    enrichment_service: DataEnrichmentService = Depends(get_enrichment_service),
) -> Any:
    """
    Get enhanced analytics insights with data processing enrichment for deeper analysis.
    
    Uses the data enrichment service to provide contextual insights, trends, and predictions.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access analytics for this organization",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
    if not end_date:
        end_date = datetime.now(timezone.utc)
    
    # Get basic analytics data
    agents = agent_service.get_agents_by_organization(db, org_id=org_id)
    agent_ids = [agent.id for agent in agents]
    
    if not agent_ids:
        base_analytics = {
            "organization_id": org_id,
            "organization_name": organization.name,
            "period": {"start_date": start_date, "end_date": end_date},
            "summary": {"total_cost": 0.0, "total_revenue": 0.0, "margin": 0.0, "activities": 0},
            "agents": {"total": 0, "active": 0}
        }
    else:
        # Query aggregate data
        activity_count = db.query(func.count(AgentActivity.id)).filter(
            AgentActivity.agent_id.in_(agent_ids),
            AgentActivity.timestamp >= start_date,
            AgentActivity.timestamp <= end_date
        ).scalar() or 0
        
        total_cost = db.query(func.sum(AgentCost.amount)).filter(
            AgentCost.agent_id.in_(agent_ids),
            AgentCost.timestamp >= start_date,
            AgentCost.timestamp <= end_date
        ).scalar() or 0.0
        
        total_revenue = db.query(func.sum(AgentOutcome.value)).filter(
            AgentOutcome.agent_id.in_(agent_ids),
            AgentOutcome.timestamp >= start_date,
            AgentOutcome.timestamp <= end_date
        ).scalar() or 0.0
        
        margin = (total_revenue - total_cost) if total_revenue > 0 else 0.0
        active_agents = db.query(func.count(Agent.id)).filter(
            Agent.organization_id == org_id,
            Agent.is_active == True
        ).scalar() or 0
        
        base_analytics = {
            "organization_id": org_id,
            "organization_name": organization.name,
            "period": {"start_date": start_date, "end_date": end_date},
            "summary": {
                "total_cost": float(total_cost),
                "total_revenue": float(total_revenue),
                "margin": float(margin),
                "activities": activity_count
            },
            "agents": {"total": len(agents), "active": active_agents}
        }
    
    # Define enrichment rules for analytics insights
    enrichment_rules = [
        EnrichmentRule(
            name="trend_analysis",
            enrichment_type=EnrichmentType.CALCULATION,
            source_fields=["summary"],
            target_fields=["trends"],
            parameters={
                "analysis_type": "time_series",
                "period_days": (end_date - start_date).days,
                "calculate_growth_rate": True
            },
            priority=EnrichmentPriority.HIGH,
            description="Analyze trends and growth patterns"
        ),
        EnrichmentRule(
            name="performance_insights",
            enrichment_type=EnrichmentType.CONTEXTUAL,
            source_fields=["summary", "agents"],
            target_fields=["insights"],
            parameters={
                "generate_recommendations": True,
                "benchmark_comparison": True,
                "efficiency_analysis": True
            },
            priority=EnrichmentPriority.MEDIUM,
            description="Generate performance insights and recommendations"
        ),
        EnrichmentRule(
            name="predictive_analytics",
            enrichment_type=EnrichmentType.ML_PREDICTION,
            source_fields=["summary", "trends"],
            target_fields=["predictions"],
            parameters={
                "forecast_horizon_days": 30,
                "confidence_interval": 0.95,
                "include_seasonality": True
            },
            priority=EnrichmentPriority.LOW,
            description="Generate predictive analytics and forecasts"
        )
    ]
    
    try:
        # Apply enrichment to analytics data
        enrichment_result = await enrichment_service.enrich_data(
            base_analytics, 
            enrichment_rules, 
            validate_input=False
        )
        
        if enrichment_result.success and enrichment_result.enriched_data:
            enhanced_analytics = enrichment_result.enriched_data
            enhanced_analytics["enrichment_metadata"] = {
                "processing_time": enrichment_result.processing_time,
                "cache_hit": enrichment_result.cache_hit,
                "applied_enrichments": len(enrichment_rules)
            }
        else:
            enhanced_analytics = base_analytics
            enhanced_analytics["enrichment_metadata"] = {
                "processing_time": None,
                "cache_hit": False,
                "applied_enrichments": 0,
                "errors": enrichment_result.errors if hasattr(enrichment_result, 'errors') else []
            }
    except Exception as e:
        logger.warning(f"Failed to enrich analytics data: {e}")
        enhanced_analytics = base_analytics
        enhanced_analytics["enrichment_metadata"] = {
            "processing_time": None,
            "cache_hit": False,
            "applied_enrichments": 0,
            "error": str(e)
        }
    
    return enhanced_analytics