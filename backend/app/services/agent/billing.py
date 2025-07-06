"""
Billing operations for agents.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.billing_model.calculation import calculate_cost
from .core import get_agent

def get_agent_billing_config(db: Session, agent_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the billing configuration for an agent
    """
    agent = get_agent(db, agent_id=agent_id)
    if not agent or not agent.billing_model:
        return None
    
    bm = agent.billing_model
    config = {
        "model_type": bm.model_type,
        "model_id": bm.id,
        "model_name": bm.name,
        "is_active": bm.is_active
    }
    
    # Add type-specific config
    if bm.model_type == "agent" and bm.agent_config:
        config["agent_config"] = {
            "base_agent_fee": bm.agent_config.base_agent_fee,
            "billing_frequency": bm.agent_config.billing_frequency,
            "agent_tier": bm.agent_config.agent_tier
        }
    elif bm.model_type == "activity" and bm.activity_config:
        config["activity_configs"] = [
            {
                "activity_type": cfg.activity_type,
                "price_per_unit": cfg.price_per_unit,
                "unit_type": cfg.unit_type,
                "is_active": cfg.is_active
            } for cfg in bm.activity_config
        ]
    elif bm.model_type == "outcome" and bm.outcome_config:
        config["outcome_configs"] = [
            {
                "outcome_type": cfg.outcome_type,
                "outcome_name": cfg.outcome_name,
                "percentage": cfg.percentage,
                "requires_verification": cfg.requires_verification,
                "is_active": cfg.is_active
            } for cfg in bm.outcome_config
        ]
    elif bm.model_type == "workflow" and bm.workflow_types:
        config["workflow_config"] = {
            "base_platform_fee": bm.workflow_config.base_platform_fee,
            "platform_fee_frequency": bm.workflow_config.platform_fee_frequency,
            "default_billing_frequency": bm.workflow_config.default_billing_frequency,
            "currency": bm.workflow_config.currency,
            "volume_discount_enabled": bm.workflow_config.volume_discount_enabled,
            "volume_discount_threshold": bm.workflow_config.volume_discount_threshold,
            "volume_discount_percentage": bm.workflow_config.volume_discount_percentage,
            "overage_multiplier": bm.workflow_config.overage_multiplier,
            "is_active": bm.workflow_config.is_active
        }
        config["workflow_types"] = [
            {
                "workflow_type": wt.workflow_type,
                "workflow_name": wt.workflow_name,
                "description": wt.description,
                "price_per_workflow": wt.price_per_workflow,
                "complexity_level": wt.complexity_level,
                "estimated_compute_cost": wt.estimated_compute_cost,
                "estimated_duration_minutes": wt.estimated_duration_minutes,
                "expected_roi_multiplier": wt.expected_roi_multiplier,
                "business_value_category": wt.business_value_category,
                "volume_tier_1_threshold": wt.volume_tier_1_threshold,
                "volume_tier_1_price": wt.volume_tier_1_price,
                "volume_tier_2_threshold": wt.volume_tier_2_threshold,
                "volume_tier_2_price": wt.volume_tier_2_price,
                "volume_tier_3_threshold": wt.volume_tier_3_threshold,
                "volume_tier_3_price": wt.volume_tier_3_price,
                "billing_frequency": wt.billing_frequency,
                "minimum_charge": wt.minimum_charge,
                "is_active": wt.is_active
            } for wt in bm.workflow_types
        ]
        if bm.commitment_tiers:
            config["commitment_tiers"] = [
                {
                    "tier_name": ct.tier_name,
                    "tier_level": ct.tier_level,
                    "description": ct.description,
                    "minimum_workflows_per_month": ct.minimum_workflows_per_month,
                    "minimum_monthly_revenue": ct.minimum_monthly_revenue,
                    "included_workflows": ct.included_workflows,
                    "included_workflow_types": ct.included_workflow_types,
                    "discount_percentage": ct.discount_percentage,
                    "platform_fee_discount": ct.platform_fee_discount,
                    "commitment_period_months": ct.commitment_period_months,
                    "overage_rate_multiplier": ct.overage_rate_multiplier,
                    "is_active": ct.is_active,
                    "is_popular": ct.is_popular
                } for ct in bm.commitment_tiers
            ]
    
    return config


def validate_agent_billing_data(db: Session, agent_id: int, data_type: str, data: Dict[str, Any]) -> bool:
    """
    Validate that billing data matches the agent's billing model configuration
    """
    config = get_agent_billing_config(db, agent_id)
    if not config:
        return False
    
    model_type = config["model_type"]
    
    if data_type == "activity":
        if model_type != "activity":
            return False
        
        activity_type = data.get("activity_type")
        if not activity_type:
            return False
        
        # Check if activity type is configured
        activity_configs = config.get("activity_configs", [])
        return any(cfg["activity_type"] == activity_type for cfg in activity_configs)
    
    elif data_type == "outcome":
        if model_type != "outcome":
            return False
        
        outcome_type = data.get("outcome_type")
        if not outcome_type:
            return False
        
        # Check if outcome type is configured
        if model_type == "outcome":
            outcome_configs = config.get("outcome_configs", [])
            return any(cfg["outcome_type"] == outcome_type for cfg in outcome_configs)
    
    elif data_type == "workflow":
        if model_type != "workflow":
            return False
        
        workflow_type = data.get("workflow_type")
        if not workflow_type:
            return False
        
        # Check if workflow type is configured
        workflow_types = config.get("workflow_types", [])
        return any(wt["workflow_type"] == workflow_type for wt in workflow_types)
    
    return False


def validate_workflow_billing_data(db: Session, agent_id: int, workflow_executions: Dict[str, int]) -> Dict[str, Any]:
    """
    Validate workflow execution data against agent's billing model
    
    Args:
        agent_id: ID of the agent
        workflow_executions: Dictionary mapping workflow types to execution counts
    
    Returns:
        Dictionary with validation results
    """
    # Check if agent exists
    agent = get_agent(db, agent_id=agent_id)
    if not agent:
        return {"valid": False, "error": f"Agent with ID {agent_id} not found"}
    
    # Check billing model
    bm = agent.billing_model
    if not bm or bm.model_type != "workflow":
        return {"valid": False, "error": f"Agent {agent_id} does not have a workflow billing model"}
    
    # Validate each workflow type
    validation_results = {
        "valid": True,
        "workflow_validations": {},
        "warnings": [],
        "total_estimated_cost": 0.0
    }
    
    configured_workflow_types = {wt.workflow_type for wt in bm.workflow_types if wt.is_active}
    
    for workflow_type, count in workflow_executions.items():
        workflow_validation = {
            "valid": True,
            "configured": workflow_type in configured_workflow_types,
            "count": count,
            "estimated_cost": 0.0
        }
        
        if not workflow_validation["configured"]:
            workflow_validation["valid"] = False
            workflow_validation["error"] = f"Workflow type '{workflow_type}' is not configured for this agent"
            validation_results["valid"] = False
        else:
            # Calculate estimated cost
            try:
                usage_data = {"workflows": {workflow_type: count}}
                estimated_cost = calculate_cost(bm, usage_data)
                workflow_validation["estimated_cost"] = estimated_cost
                validation_results["total_estimated_cost"] += estimated_cost
            except Exception as e:
                workflow_validation["valid"] = False
                workflow_validation["error"] = f"Failed to calculate cost: {str(e)}"
                validation_results["valid"] = False
        
        validation_results["workflow_validations"][workflow_type] = workflow_validation
    
    # Add warnings for inactive workflow types
    for workflow_type in workflow_executions.keys():
        if workflow_type in configured_workflow_types:
            workflow_config = next((wt for wt in bm.workflow_types if wt.workflow_type == workflow_type), None)
            if workflow_config and not workflow_config.is_active:
                validation_results["warnings"].append(f"Workflow type '{workflow_type}' is configured but not active")
    
    return validation_results
