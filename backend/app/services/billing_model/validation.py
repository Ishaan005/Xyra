"""
Validation logic for billing models.
"""
from typing import Optional


def validate_billing_config_from_schema(billing_model_in, current_model_type: Optional[str] = None) -> None:
    """
    Validate billing model configuration based on schema fields
    """
    # For update operations, model_type might not be present in the schema
    # In that case, use the current_model_type parameter
    if hasattr(billing_model_in, 'model_type') and billing_model_in.model_type is not None:
        model_type = billing_model_in.model_type
    elif current_model_type is not None:
        model_type = current_model_type
    else:
        # If no model_type available, skip validation (shouldn't happen in normal flow)
        return
    
    if model_type == "agent":
        if billing_model_in.agent_base_agent_fee is None or billing_model_in.agent_base_agent_fee <= 0:
            raise ValueError("Agent-based billing model must include a positive 'agent_base_agent_fee'")
        
        if billing_model_in.agent_billing_frequency and billing_model_in.agent_billing_frequency not in ["monthly", "yearly"]:
            raise ValueError("'agent_billing_frequency' must be one of: monthly, yearly")
        
        if billing_model_in.agent_volume_discount_enabled:
            if billing_model_in.agent_volume_discount_threshold is None or billing_model_in.agent_volume_discount_threshold <= 0:
                raise ValueError("Volume discount requires a positive 'agent_volume_discount_threshold'")
            if billing_model_in.agent_volume_discount_percentage is None or billing_model_in.agent_volume_discount_percentage <= 0:
                raise ValueError("Volume discount requires a positive 'agent_volume_discount_percentage'")
        
        if billing_model_in.agent_tier and billing_model_in.agent_tier not in ["starter", "professional", "enterprise"]:
            raise ValueError("'agent_tier' must be one of: starter, professional, enterprise")
        
    elif model_type == "activity":
        if billing_model_in.activity_price_per_unit is None or billing_model_in.activity_price_per_unit <= 0:
            raise ValueError("Activity-based billing model must include a positive 'activity_price_per_unit'")
        
        if not billing_model_in.activity_activity_type:
            raise ValueError("Activity-based billing model must include 'activity_activity_type'")
        
        if billing_model_in.activity_unit_type and billing_model_in.activity_unit_type not in ["action", "token", "minute", "request", "query", "completion"]:
            raise ValueError("'activity_unit_type' must be one of: action, token, minute, request, query, completion")
        
        if billing_model_in.activity_billing_frequency and billing_model_in.activity_billing_frequency not in ["monthly", "daily", "per_use"]:
            raise ValueError("'activity_billing_frequency' must be one of: monthly, daily, per_use")
        
        # Validate volume pricing tiers if enabled
        if billing_model_in.activity_volume_pricing_enabled:
            tier_configs = [
                (billing_model_in.activity_volume_tier_1_threshold, billing_model_in.activity_volume_tier_1_price, "tier 1"),
                (billing_model_in.activity_volume_tier_2_threshold, billing_model_in.activity_volume_tier_2_price, "tier 2"),
                (billing_model_in.activity_volume_tier_3_threshold, billing_model_in.activity_volume_tier_3_price, "tier 3"),
            ]
            
            # Check that at least one tier is configured
            has_any_tier = any(threshold is not None and price is not None for threshold, price, _ in tier_configs)
            if not has_any_tier:
                raise ValueError("Volume pricing enabled but no valid pricing tiers configured")
            
            # Validate each configured tier
            previous_threshold = 0
            for threshold, price, tier_name in tier_configs:
                if threshold is not None and price is not None:
                    if threshold <= previous_threshold:
                        raise ValueError(f"Volume pricing {tier_name} threshold must be greater than previous tier")
                    if price < 0:
                        raise ValueError(f"Volume pricing {tier_name} price must be non-negative")
                    previous_threshold = threshold
    
    elif model_type == "outcome":
        if not billing_model_in.outcome_outcome_type:
            raise ValueError("Outcome-based billing model must include 'outcome_outcome_type'")
        
        if billing_model_in.outcome_percentage is None or billing_model_in.outcome_percentage <= 0:
            raise ValueError("Outcome-based billing model must include a positive 'outcome_percentage'")
    
    elif model_type == "hybrid":
        # Hybrid must have at least one billing component
        has_base_fee = billing_model_in.hybrid_base_fee is not None and billing_model_in.hybrid_base_fee >= 0
        has_agent = billing_model_in.hybrid_agent_config is not None
        has_activity = billing_model_in.hybrid_activity_configs is not None and len(billing_model_in.hybrid_activity_configs) > 0
        has_outcome = billing_model_in.hybrid_outcome_configs is not None and len(billing_model_in.hybrid_outcome_configs) > 0
        
        if not any([has_base_fee, has_agent, has_activity, has_outcome]):
            raise ValueError("Hybrid billing model must include at least one billing component")
        
        # Validate each component if present
        if has_agent:
            if billing_model_in.hybrid_agent_config.base_agent_fee <= 0:
                raise ValueError("Agent configuration must include a positive 'base_agent_fee'")
            if billing_model_in.hybrid_agent_config.volume_discount_enabled:
                if (billing_model_in.hybrid_agent_config.volume_discount_threshold is None or 
                    billing_model_in.hybrid_agent_config.volume_discount_threshold <= 0):
                    raise ValueError("Volume discount requires a positive 'volume_discount_threshold'")
                if (billing_model_in.hybrid_agent_config.volume_discount_percentage is None or 
                    billing_model_in.hybrid_agent_config.volume_discount_percentage <= 0):
                    raise ValueError("Volume discount requires a positive 'volume_discount_percentage'")
        
        if has_activity:
            for activity in billing_model_in.hybrid_activity_configs:
                if activity.price_per_unit <= 0 or not activity.activity_type:
                    raise ValueError("Each activity configuration must include positive 'price_per_unit' and 'activity_type'")
        
        if has_outcome:
            for outcome in billing_model_in.hybrid_outcome_configs:
                if not outcome.outcome_type or outcome.percentage <= 0:
                    raise ValueError("Each outcome configuration must include 'outcome_type' and positive 'percentage'")
    
    elif model_type == "workflow":
        # Workflow must have at least a base config or one workflow type
        has_base_config = billing_model_in.workflow_base_platform_fee is not None and billing_model_in.workflow_base_platform_fee >= 0
        has_workflow_types = billing_model_in.workflow_types is not None and len(billing_model_in.workflow_types) > 0
        
        if not (has_base_config or has_workflow_types):
            raise ValueError("Workflow billing model must include at least a base config or one workflow type")
        
        # Validate workflow types if present
        if has_workflow_types:
            for workflow_type in billing_model_in.workflow_types:
                if workflow_type.price_per_workflow <= 0 or not workflow_type.workflow_name:
                    raise ValueError("Each workflow type configuration must include positive 'price_per_workflow' and 'workflow_name'")
    
    return
