from typing import Dict, Any
from app.models.billing_model import BillingModel

def calculate_cost(billing_model: BillingModel, usage_data: Dict[str, Any]) -> float:
    """
    Calculate cost based on billing model and usage data using dedicated config tables
    """
    # Use dedicated config tables via relationships
    total_cost = 0.0
    current_model_type = str(billing_model.model_type)
    
    if current_model_type == "agent":
        # Expect one AgentBasedConfig row
        if billing_model.agent_config:
            cfg = billing_model.agent_config
            agents = usage_data.get("agents", 1)  # Default to 1 agent
            
            # Calculate base cost
            base_cost = cfg.base_agent_fee * agents
            
            # Add setup fee (one-time, so only if usage_data indicates this is initial billing)
            if usage_data.get("include_setup_fee", False):
                base_cost += cfg.setup_fee
            
            # Apply volume discount if enabled and threshold met
            if cfg.volume_discount_enabled and agents >= (cfg.volume_discount_threshold or 0):
                discount = base_cost * (cfg.volume_discount_percentage or 0) / 100.0
                base_cost -= discount
            
            total_cost = base_cost
    elif current_model_type == "activity":
        # Enhanced activity-based billing with volume pricing and base agent fees
        units_used = usage_data.get("units", 0)  # Generic units (actions, tokens, etc.)
        agents = usage_data.get("agents", 1)  # Number of agents for base fee calculation
        
        for cfg in billing_model.activity_config:
            if not cfg.is_active:
                continue
                
            activity_cost = 0.0
            
            # Add base agent fee if configured
            if cfg.base_agent_fee > 0:
                activity_cost += cfg.base_agent_fee * agents
            
            # Calculate unit-based cost with volume pricing
            if cfg.volume_pricing_enabled and units_used > 0:
                # Apply tiered pricing
                remaining_units = units_used
                
                # Tier 1
                if cfg.volume_tier_1_threshold and cfg.volume_tier_1_price is not None and remaining_units > 0:
                    tier_1_units = min(remaining_units, cfg.volume_tier_1_threshold)
                    if tier_1_units > 0:
                        activity_cost += tier_1_units * cfg.volume_tier_1_price
                        remaining_units -= tier_1_units
                
                # Tier 2
                if (cfg.volume_tier_2_threshold and cfg.volume_tier_2_price is not None and 
                    remaining_units > 0 and cfg.volume_tier_1_threshold):
                    tier_2_units = min(remaining_units, cfg.volume_tier_2_threshold - cfg.volume_tier_1_threshold)
                    if tier_2_units > 0:
                        activity_cost += tier_2_units * cfg.volume_tier_2_price
                        remaining_units -= tier_2_units
                
                # Tier 3
                if (cfg.volume_tier_3_threshold and cfg.volume_tier_3_price is not None and 
                    remaining_units > 0 and cfg.volume_tier_2_threshold):
                    tier_3_units = min(remaining_units, cfg.volume_tier_3_threshold - cfg.volume_tier_2_threshold)
                    if tier_3_units > 0:
                        activity_cost += tier_3_units * cfg.volume_tier_3_price
                        remaining_units -= tier_3_units
                
                # Any remaining units use the highest tier price or base price
                if remaining_units > 0:
                    final_price = cfg.volume_tier_3_price if cfg.volume_tier_3_price is not None else cfg.price_per_unit
                    activity_cost += remaining_units * final_price
            else:
                # Simple unit-based pricing
                activity_cost += cfg.price_per_unit * units_used
            
            # Apply minimum charge if configured
            if cfg.minimum_charge > 0:
                activity_cost = max(activity_cost, cfg.minimum_charge)
                
            total_cost += activity_cost
    elif current_model_type == "outcome":
        # Outcome-based billing: percentage of outcome_value
        outcome_value = usage_data.get("outcome_value", 0)
        for cfg in billing_model.outcome_config:
            total_cost += (cfg.percentage / 100.0) * outcome_value
    elif current_model_type == "hybrid":
        # Hybrid: base fee from dedicated config table, plus each component
        # Base fee from HybridConfig
        if billing_model.hybrid_config:
            total_cost += billing_model.hybrid_config.base_fee
        # Agent
        if hasattr(billing_model, "agent_config") and billing_model.agent_config:
            agents = usage_data.get("agents", 1)
            cfg = billing_model.agent_config
            
            # Calculate base cost
            agent_cost = cfg.base_agent_fee * agents
            
            # Add setup fee if applicable
            if usage_data.get("include_setup_fee", False):
                agent_cost += cfg.setup_fee
            
            # Apply volume discount if enabled and threshold met
            if cfg.volume_discount_enabled and agents >= (cfg.volume_discount_threshold or 0):
                discount = agent_cost * (cfg.volume_discount_percentage or 0) / 100.0
                agent_cost -= discount
            
            total_cost += agent_cost
        # Activity - use the same enhanced logic as pure activity model
        units_used = usage_data.get("units", 0)
        agents = usage_data.get("agents", 1)
        
        for cfg in billing_model.activity_config:
            if not cfg.is_active:
                continue
                
            activity_cost = 0.0
            
            # Add base agent fee if configured
            if cfg.base_agent_fee > 0:
                activity_cost += cfg.base_agent_fee * agents
            
            # Calculate unit-based cost with volume pricing
            if cfg.volume_pricing_enabled and units_used > 0:
                # Apply tiered pricing
                remaining_units = units_used
                
                # Tier 1
                if cfg.volume_tier_1_threshold and cfg.volume_tier_1_price is not None and remaining_units > 0:
                    tier_1_units = min(remaining_units, cfg.volume_tier_1_threshold)
                    if tier_1_units > 0:
                        activity_cost += tier_1_units * cfg.volume_tier_1_price
                        remaining_units -= tier_1_units
                
                # Tier 2
                if (cfg.volume_tier_2_threshold and cfg.volume_tier_2_price is not None and 
                    remaining_units > 0 and cfg.volume_tier_1_threshold):
                    tier_2_units = min(remaining_units, cfg.volume_tier_2_threshold - cfg.volume_tier_1_threshold)
                    if tier_2_units > 0:
                        activity_cost += tier_2_units * cfg.volume_tier_2_price
                        remaining_units -= tier_2_units
                
                # Tier 3
                if (cfg.volume_tier_3_threshold and cfg.volume_tier_3_price is not None and 
                    remaining_units > 0 and cfg.volume_tier_2_threshold):
                    tier_3_units = min(remaining_units, cfg.volume_tier_3_threshold - cfg.volume_tier_2_threshold)
                    if tier_3_units > 0:
                        activity_cost += tier_3_units * cfg.volume_tier_3_price
                        remaining_units -= tier_3_units
                
                # Any remaining units use the highest tier price or base price
                if remaining_units > 0:
                    final_price = cfg.volume_tier_3_price if cfg.volume_tier_3_price is not None else cfg.price_per_unit
                    activity_cost += remaining_units * final_price
            else:
                # Simple unit-based pricing
                activity_cost += cfg.price_per_unit * units_used
            
            # Apply minimum charge if configured
            if cfg.minimum_charge > 0:
                activity_cost = max(activity_cost, cfg.minimum_charge)
                
            total_cost += activity_cost
        # Outcome
        outcome_value = usage_data.get("outcome_value", 0)
        for cfg in billing_model.outcome_config:
            total_cost += (cfg.percentage / 100.0) * outcome_value
    elif current_model_type == "workflow":
        # Workflow-based billing: base platform fee plus individual workflow pricing
        if billing_model.workflow_config:
            cfg = billing_model.workflow_config
            
            # Add base platform fee (subscription component)
            total_cost += cfg.base_platform_fee
            
            # Process each workflow type
            workflow_usage = usage_data.get("workflows", {})  # Expected format: {"lead_research": 10, "financial_forecast": 5}
            
            for workflow_type in billing_model.workflow_types:
                if not workflow_type.is_active:
                    continue
                
                workflow_count = workflow_usage.get(workflow_type.workflow_type, 0)
                if workflow_count <= 0:
                    continue
                
                workflow_cost = 0.0
                
                # Apply volume pricing if configured for this workflow type
                if (workflow_type.volume_tier_1_threshold and workflow_type.volume_tier_1_price is not None and 
                    workflow_count > 0):
                    remaining_workflows = workflow_count
                    
                    # Tier 1 - first workflows up to tier 1 threshold get tier 1 price
                    tier_1_workflows = min(remaining_workflows, workflow_type.volume_tier_1_threshold)
                    workflow_cost += tier_1_workflows * workflow_type.volume_tier_1_price
                    remaining_workflows -= tier_1_workflows
                    
                    # Tier 2
                    if (workflow_type.volume_tier_2_threshold and workflow_type.volume_tier_2_price is not None and 
                        remaining_workflows > 0):
                        tier_2_workflows = min(remaining_workflows, 
                                             workflow_type.volume_tier_2_threshold - workflow_type.volume_tier_1_threshold)
                        workflow_cost += tier_2_workflows * workflow_type.volume_tier_2_price
                        remaining_workflows -= tier_2_workflows
                    
                    # Tier 3
                    if (workflow_type.volume_tier_3_threshold and workflow_type.volume_tier_3_price is not None and 
                        remaining_workflows > 0):
                        tier_3_workflows = min(remaining_workflows, 
                                             workflow_type.volume_tier_3_threshold - workflow_type.volume_tier_2_threshold)
                        workflow_cost += tier_3_workflows * workflow_type.volume_tier_3_price
                        remaining_workflows -= tier_3_workflows
                    
                    # Any remaining workflows use the highest tier price or base price
                    if remaining_workflows > 0:
                        final_price = (workflow_type.volume_tier_3_price if workflow_type.volume_tier_3_price is not None 
                                     else workflow_type.price_per_workflow)
                        workflow_cost += remaining_workflows * final_price
                else:
                    # Simple per-workflow pricing
                    workflow_cost = workflow_type.price_per_workflow * workflow_count
                
                # Apply minimum charge if configured
                if workflow_type.minimum_charge and workflow_type.minimum_charge > 0:
                    workflow_cost = max(workflow_cost, workflow_type.minimum_charge)
                
                # Apply overage multiplier if this is beyond commitment
                commitment_exceeded = usage_data.get("commitment_exceeded", False)
                if commitment_exceeded and cfg.overage_multiplier > 1.0:
                    workflow_cost *= cfg.overage_multiplier
                
                total_cost += workflow_cost
            
            # Apply global volume discount if enabled
            total_workflows = sum(workflow_usage.values())
            if (cfg.volume_discount_enabled and total_workflows >= (cfg.volume_discount_threshold or 0) and 
                cfg.volume_discount_percentage):
                discount = total_cost * (cfg.volume_discount_percentage / 100.0)
                total_cost -= discount
    return total_cost