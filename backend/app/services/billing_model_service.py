from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session, joinedload

from app.models.billing_model import BillingModel
from app.models.organization import Organization
from app.schemas.billing_model import BillingModelCreate, BillingModelUpdate
from app.services.billing_model.validation import validate_billing_config_from_schema

# Configure logging
logger = logging.getLogger(__name__)


def get_billing_model(db: Session, model_id: int) -> Optional[BillingModel]:
    """
    Get billing model by ID with eagerly loaded relationships
    """
    return (
        db.query(BillingModel)
        .options(
            joinedload(BillingModel.agent_config),
            joinedload(BillingModel.activity_config),
            joinedload(BillingModel.outcome_config),
            joinedload(BillingModel.hybrid_config),
            joinedload(BillingModel.workflow_config),
            joinedload(BillingModel.workflow_types),
            joinedload(BillingModel.commitment_tiers)
        )
        .filter(BillingModel.id == model_id)
        .first()
    )


def get_billing_models_by_organization(
    db: Session, org_id: int, skip: int = 0, limit: int = 100
) -> List[BillingModel]:
    """
    Get all billing models for an organization with pagination and eagerly loaded relationships
    """
    return (
        db.query(BillingModel)
        .options(
            joinedload(BillingModel.agent_config),
            joinedload(BillingModel.activity_config),
            joinedload(BillingModel.outcome_config),
            joinedload(BillingModel.hybrid_config),
            joinedload(BillingModel.workflow_config),
            joinedload(BillingModel.workflow_types),
            joinedload(BillingModel.commitment_tiers)
        )
        .filter(BillingModel.organization_id == org_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_billing_model(db: Session, billing_model_in: BillingModelCreate) -> BillingModel:
    """
    Create a new billing model for an organization
    """
    # Check if organization exists
    organization = db.query(Organization).filter(
        Organization.id == billing_model_in.organization_id
    ).first()
    
    if not organization:
        raise ValueError(f"Organization with ID {billing_model_in.organization_id} not found")
    
    # Validate billing model type
    valid_types = ["agent", "activity", "outcome", "hybrid", "workflow"]
    if billing_model_in.model_type not in valid_types:
        raise ValueError(
            f"Invalid billing model type: {billing_model_in.model_type}. "
            f"Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate config based on model type and input fields
    validate_billing_config_from_schema(billing_model_in)
    
    # Create billing model
    billing_model = BillingModel(
        name=billing_model_in.name,
        description=billing_model_in.description,
        organization_id=billing_model_in.organization_id,
        model_type=billing_model_in.model_type,
        is_active=billing_model_in.is_active,
    )
    
    # Add billing model to database
    db.add(billing_model)
    db.commit()
    db.refresh(billing_model)

    # Persist config into dedicated tables
    from app.models.billing_model import AgentBasedConfig, ActivityBasedConfig, OutcomeBasedConfig, HybridConfig, WorkflowBasedConfig, WorkflowType, CommitmentTier
    
    if billing_model_in.model_type == "agent":
        agent_cfg = AgentBasedConfig(
            billing_model_id=billing_model.id,
            base_agent_fee=billing_model_in.agent_base_agent_fee,
            billing_frequency=billing_model_in.agent_billing_frequency,
            setup_fee=billing_model_in.agent_setup_fee or 0.0,
            volume_discount_enabled=billing_model_in.agent_volume_discount_enabled or False,
            volume_discount_threshold=billing_model_in.agent_volume_discount_threshold,
            volume_discount_percentage=billing_model_in.agent_volume_discount_percentage,
            agent_tier=billing_model_in.agent_tier or "professional",
        )
        db.add(agent_cfg)
    elif billing_model_in.model_type == "activity":
        act_cfg = ActivityBasedConfig(
            billing_model_id=billing_model.id,
            price_per_unit=billing_model_in.activity_price_per_unit,
            activity_type=billing_model_in.activity_activity_type,
            unit_type=billing_model_in.activity_unit_type or "action",
            base_agent_fee=billing_model_in.activity_base_agent_fee or 0.0,
            volume_pricing_enabled=billing_model_in.activity_volume_pricing_enabled or False,
            volume_tier_1_threshold=billing_model_in.activity_volume_tier_1_threshold,
            volume_tier_1_price=billing_model_in.activity_volume_tier_1_price,
            volume_tier_2_threshold=billing_model_in.activity_volume_tier_2_threshold,
            volume_tier_2_price=billing_model_in.activity_volume_tier_2_price,
            volume_tier_3_threshold=billing_model_in.activity_volume_tier_3_threshold,
            volume_tier_3_price=billing_model_in.activity_volume_tier_3_price,
            minimum_charge=billing_model_in.activity_minimum_charge or 0.0,
            billing_frequency=billing_model_in.activity_billing_frequency or "monthly",
            is_active=billing_model_in.activity_is_active or True,
        )
        db.add(act_cfg)
    elif billing_model_in.model_type == "outcome":
        out_cfg = OutcomeBasedConfig(
            billing_model_id=billing_model.id,
            outcome_type=billing_model_in.outcome_outcome_type,
            percentage=billing_model_in.outcome_percentage,
        )
        db.add(out_cfg)
    elif billing_model_in.model_type == "hybrid":
        # Create hybrid base config
        if billing_model_in.hybrid_base_fee is not None:
            hybrid_cfg = HybridConfig(
                billing_model_id=billing_model.id,
                base_fee=billing_model_in.hybrid_base_fee,
            )
            db.add(hybrid_cfg)
        
        # Create agent config if provided
        if billing_model_in.hybrid_agent_config:
            agent_cfg = AgentBasedConfig(
                billing_model_id=billing_model.id,
                base_agent_fee=billing_model_in.hybrid_agent_config.base_agent_fee,
                billing_frequency=billing_model_in.hybrid_agent_config.billing_frequency,
                setup_fee=billing_model_in.hybrid_agent_config.setup_fee or 0.0,
                volume_discount_enabled=billing_model_in.hybrid_agent_config.volume_discount_enabled or False,
                volume_discount_threshold=billing_model_in.hybrid_agent_config.volume_discount_threshold,
                volume_discount_percentage=billing_model_in.hybrid_agent_config.volume_discount_percentage,
                agent_tier=billing_model_in.hybrid_agent_config.agent_tier or "professional",
            )
            db.add(agent_cfg)
            
        # Create activity configs if provided
        if billing_model_in.hybrid_activity_configs:
            for ac in billing_model_in.hybrid_activity_configs:
                act_cfg = ActivityBasedConfig(
                    billing_model_id=billing_model.id,
                    price_per_unit=ac.price_per_unit,
                    activity_type=ac.activity_type,
                    unit_type=ac.unit_type or "action",
                    base_agent_fee=ac.base_agent_fee or 0.0,
                    volume_pricing_enabled=ac.volume_pricing_enabled or False,
                    volume_tier_1_threshold=ac.volume_tier_1_threshold,
                    volume_tier_1_price=ac.volume_tier_1_price,
                    volume_tier_2_threshold=ac.volume_tier_2_threshold,
                    volume_tier_2_price=ac.volume_tier_2_price,
                    volume_tier_3_threshold=ac.volume_tier_3_threshold,
                    volume_tier_3_price=ac.volume_tier_3_price,
                    minimum_charge=ac.minimum_charge or 0.0,
                    billing_frequency=ac.billing_frequency or "monthly",
                    is_active=ac.is_active or True,
                )
                db.add(act_cfg)
                
        # Create outcome configs if provided
        if billing_model_in.hybrid_outcome_configs:
            for oc in billing_model_in.hybrid_outcome_configs:
                out_cfg = OutcomeBasedConfig(
                    billing_model_id=billing_model.id,
                    outcome_type=oc.outcome_type,
                    percentage=oc.percentage,
                )
                db.add(out_cfg)
    elif billing_model_in.model_type == "workflow":
        # Create workflow base config
        from app.models.billing_model import WorkflowBasedConfig, WorkflowType, CommitmentTier
        
        workflow_cfg = WorkflowBasedConfig(
            billing_model_id=billing_model.id,
            base_platform_fee=billing_model_in.workflow_base_platform_fee or 0.0,
            platform_fee_frequency=billing_model_in.workflow_platform_fee_frequency or "monthly",
            default_billing_frequency=billing_model_in.workflow_default_billing_frequency or "monthly",
            volume_discount_enabled=billing_model_in.workflow_volume_discount_enabled or False,
            volume_discount_threshold=billing_model_in.workflow_volume_discount_threshold,
            volume_discount_percentage=billing_model_in.workflow_volume_discount_percentage,
            overage_multiplier=billing_model_in.workflow_overage_multiplier or 1.0,
            currency=billing_model_in.workflow_currency or "USD",
            is_active=billing_model_in.workflow_is_active or True,
        )
        db.add(workflow_cfg)
        
        # Create workflow types if provided
        if billing_model_in.workflow_types:
            for wt in billing_model_in.workflow_types:
                workflow_type = WorkflowType(
                    billing_model_id=billing_model.id,
                    workflow_name=wt.workflow_name,
                    workflow_type=wt.workflow_type,
                    description=wt.description,
                    price_per_workflow=wt.price_per_workflow,
                    estimated_compute_cost=wt.estimated_compute_cost or 0.0,
                    estimated_duration_minutes=wt.estimated_duration_minutes,
                    complexity_level=wt.complexity_level or "medium",
                    expected_roi_multiplier=wt.expected_roi_multiplier,
                    business_value_category=wt.business_value_category,
                    volume_tier_1_threshold=wt.volume_tier_1_threshold,
                    volume_tier_1_price=wt.volume_tier_1_price,
                    volume_tier_2_threshold=wt.volume_tier_2_threshold,
                    volume_tier_2_price=wt.volume_tier_2_price,
                    volume_tier_3_threshold=wt.volume_tier_3_threshold,
                    volume_tier_3_price=wt.volume_tier_3_price,
                    billing_frequency=wt.billing_frequency,
                    minimum_charge=wt.minimum_charge or 0.0,
                    is_active=wt.is_active or True,
                )
                db.add(workflow_type)
        
        # Create commitment tiers if provided
        if billing_model_in.commitment_tiers:
            for ct in billing_model_in.commitment_tiers:
                commitment_tier = CommitmentTier(
                    billing_model_id=billing_model.id,
                    tier_name=ct.tier_name,
                    tier_level=ct.tier_level,
                    description=ct.description,
                    minimum_workflows_per_month=ct.minimum_workflows_per_month,
                    minimum_monthly_revenue=ct.minimum_monthly_revenue,
                    included_workflows=ct.included_workflows or 0,
                    included_workflow_types=ct.included_workflow_types,
                    discount_percentage=ct.discount_percentage or 0.0,
                    platform_fee_discount=ct.platform_fee_discount or 0.0,
                    commitment_period_months=ct.commitment_period_months or 12,
                    overage_rate_multiplier=ct.overage_rate_multiplier or 1.0,
                    is_active=ct.is_active or True,
                    is_popular=ct.is_popular or False,
                )
                db.add(commitment_tier)
    db.commit()
    
    # Re-fetch with eager loading to ensure relationships are available
    created_billing_model = get_billing_model(db, model_id=getattr(billing_model, 'id'))
    if not created_billing_model:
        raise ValueError("Failed to create billing model")
    
    logger.info(f"Created new billing model: {created_billing_model.name} for organization {organization.name}")
    return created_billing_model


def update_billing_model(
    db: Session, model_id: int, billing_model_in: BillingModelUpdate
) -> Optional[BillingModel]:
    """
    Update a billing model
    """
    billing_model = get_billing_model(db, model_id=model_id)
    if not billing_model:
        logger.warning(f"Billing model update failed: Model not found with ID {model_id}")
        return None
    
    # Get update data from Pydantic model, excluding unset fields
    update_data = billing_model_in.model_dump(exclude_unset=True)
    
    # Validate billing model type if being updated
    if "model_type" in update_data:
        valid_types = ["agent", "activity", "outcome", "hybrid", "workflow"]
        if update_data["model_type"] not in valid_types:
            raise ValueError(
                f"Invalid billing model type: {update_data['model_type']}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
    
    # Validate config based on model type and input fields if config fields are being updated
    if any(field in update_data for field in [
        "agent_base_agent_fee", "agent_billing_frequency", "agent_setup_fee", 
        "agent_volume_discount_enabled", "agent_volume_discount_threshold", "agent_volume_discount_percentage", "agent_tier",
        "activity_price_per_unit", "activity_activity_type", "activity_unit_type", "activity_base_agent_fee",
        "activity_volume_pricing_enabled", "activity_volume_tier_1_threshold", "activity_volume_tier_1_price",
        "activity_volume_tier_2_threshold", "activity_volume_tier_2_price", "activity_volume_tier_3_threshold", 
        "activity_volume_tier_3_price", "activity_minimum_charge", "activity_billing_frequency", "activity_is_active",
        "outcome_outcome_type", "outcome_percentage",
        "hybrid_base_fee", "hybrid_agent_config", "hybrid_activity_configs", "hybrid_outcome_configs",
        "workflow_base_platform_fee", "workflow_platform_fee_frequency", "workflow_default_billing_frequency",
        "workflow_volume_discount_enabled", "workflow_volume_discount_threshold", "workflow_volume_discount_percentage",
        "workflow_overage_multiplier", "workflow_currency", "workflow_is_active", "workflow_types", "commitment_tiers"
    ]):
        current_model_type = str(billing_model.model_type)
        validate_billing_config_from_schema(billing_model_in, current_model_type)
    
    # Handle config updates through dedicated schema fields
    config_updated = any(field in update_data for field in [
        "agent_base_agent_fee", "agent_billing_frequency", "agent_setup_fee", 
        "agent_volume_discount_enabled", "agent_volume_discount_threshold", "agent_volume_discount_percentage", "agent_tier",
        "activity_price_per_unit", "activity_activity_type", "activity_unit_type", "activity_base_agent_fee",
        "activity_volume_pricing_enabled", "activity_volume_tier_1_threshold", "activity_volume_tier_1_price",
        "activity_volume_tier_2_threshold", "activity_volume_tier_2_price", "activity_volume_tier_3_threshold", 
        "activity_volume_tier_3_price", "activity_minimum_charge", "activity_billing_frequency", "activity_is_active",
        "outcome_outcome_type", "outcome_percentage",
        "hybrid_base_fee", "hybrid_agent_config", "hybrid_activity_configs", "hybrid_outcome_configs",
        "workflow_base_platform_fee", "workflow_platform_fee_frequency", "workflow_default_billing_frequency",
        "workflow_volume_discount_enabled", "workflow_volume_discount_threshold", "workflow_volume_discount_percentage",
        "workflow_overage_multiplier", "workflow_currency", "workflow_is_active", "workflow_types", "commitment_tiers"
    ])
    
    if config_updated:
        from app.models.billing_model import AgentBasedConfig, ActivityBasedConfig, OutcomeBasedConfig, HybridConfig, WorkflowBasedConfig, WorkflowType, CommitmentTier
        
        # Get the current model type as a string value
        current_model_type = str(billing_model.model_type)
        model_type_changing = "model_type" in update_data
        new_model_type = update_data.get("model_type", current_model_type)

        # Remove old configs for this model_type and recreate
        if current_model_type in ("agent", "hybrid") or model_type_changing:
            db.query(AgentBasedConfig).filter(AgentBasedConfig.billing_model_id == model_id).delete()
        if current_model_type in ("activity", "hybrid") or model_type_changing:
            db.query(ActivityBasedConfig).filter(ActivityBasedConfig.billing_model_id == model_id).delete()
        if current_model_type in ("outcome", "hybrid") or model_type_changing:
            db.query(OutcomeBasedConfig).filter(OutcomeBasedConfig.billing_model_id == model_id).delete()
        if current_model_type == "hybrid" or model_type_changing:
            db.query(HybridConfig).filter(HybridConfig.billing_model_id == model_id).delete()
        if current_model_type == "workflow" or model_type_changing:
            db.query(WorkflowBasedConfig).filter(WorkflowBasedConfig.billing_model_id == model_id).delete()
            db.query(WorkflowType).filter(WorkflowType.billing_model_id == model_id).delete()
            db.query(CommitmentTier).filter(CommitmentTier.billing_model_id == model_id).delete()
        db.flush()
        
        # Recreate configs based on new values and model type
        if new_model_type == "agent":
            if billing_model_in.agent_base_agent_fee is not None:
                agent_cfg = AgentBasedConfig(
                    billing_model_id=model_id,
                    base_agent_fee=billing_model_in.agent_base_agent_fee,
                    billing_frequency=billing_model_in.agent_billing_frequency or "monthly",
                    setup_fee=billing_model_in.agent_setup_fee or 0.0,
                    volume_discount_enabled=billing_model_in.agent_volume_discount_enabled or False,
                    volume_discount_threshold=billing_model_in.agent_volume_discount_threshold,
                    volume_discount_percentage=billing_model_in.agent_volume_discount_percentage,
                    agent_tier=billing_model_in.agent_tier or "professional",
                )
                db.add(agent_cfg)
        elif new_model_type == "activity":
            if billing_model_in.activity_price_per_unit is not None:
                act_cfg = ActivityBasedConfig(
                    billing_model_id=model_id,
                    price_per_unit=billing_model_in.activity_price_per_unit,
                    activity_type=billing_model_in.activity_activity_type,
                    unit_type=billing_model_in.activity_unit_type or "action",
                    base_agent_fee=billing_model_in.activity_base_agent_fee or 0.0,
                    volume_pricing_enabled=billing_model_in.activity_volume_pricing_enabled or False,
                    volume_tier_1_threshold=billing_model_in.activity_volume_tier_1_threshold,
                    volume_tier_1_price=billing_model_in.activity_volume_tier_1_price,
                    volume_tier_2_threshold=billing_model_in.activity_volume_tier_2_threshold,
                    volume_tier_2_price=billing_model_in.activity_volume_tier_2_price,
                    volume_tier_3_threshold=billing_model_in.activity_volume_tier_3_threshold,
                    volume_tier_3_price=billing_model_in.activity_volume_tier_3_price,
                    minimum_charge=billing_model_in.activity_minimum_charge or 0.0,
                    billing_frequency=billing_model_in.activity_billing_frequency or "monthly",
                    is_active=billing_model_in.activity_is_active or True,
                )
                db.add(act_cfg)
        elif new_model_type == "outcome":
            if billing_model_in.outcome_outcome_type is not None:
                out_cfg = OutcomeBasedConfig(
                    billing_model_id=model_id,
                    outcome_type=billing_model_in.outcome_outcome_type,
                    percentage=billing_model_in.outcome_percentage,
                )
                db.add(out_cfg)
        elif new_model_type == "hybrid":
            # Create hybrid base config
            if billing_model_in.hybrid_base_fee is not None:
                hybrid_cfg = HybridConfig(
                    billing_model_id=model_id,
                    base_fee=billing_model_in.hybrid_base_fee,
                )
                db.add(hybrid_cfg)
            
            # Create agent config if provided
            if billing_model_in.hybrid_agent_config:
                agent_cfg = AgentBasedConfig(
                    billing_model_id=model_id,
                    base_agent_fee=billing_model_in.hybrid_agent_config.base_agent_fee,
                    billing_frequency=billing_model_in.hybrid_agent_config.billing_frequency,
                    setup_fee=billing_model_in.hybrid_agent_config.setup_fee or 0.0,
                    volume_discount_enabled=billing_model_in.hybrid_agent_config.volume_discount_enabled or False,
                    volume_discount_threshold=billing_model_in.hybrid_agent_config.volume_discount_threshold,
                    volume_discount_percentage=billing_model_in.hybrid_agent_config.volume_discount_percentage,
                    agent_tier=billing_model_in.hybrid_agent_config.agent_tier or "professional",
                )
                db.add(agent_cfg)
                
            # Create activity configs if provided
            if billing_model_in.hybrid_activity_configs:
                for ac in billing_model_in.hybrid_activity_configs:
                    act_cfg = ActivityBasedConfig(
                        billing_model_id=model_id,
                        price_per_unit=ac.price_per_unit,
                        activity_type=ac.activity_type,
                        unit_type=ac.unit_type or "action",
                        base_agent_fee=ac.base_agent_fee or 0.0,
                        volume_pricing_enabled=ac.volume_pricing_enabled or False,
                        volume_tier_1_threshold=ac.volume_tier_1_threshold,
                        volume_tier_1_price=ac.volume_tier_1_price,
                        volume_tier_2_threshold=ac.volume_tier_2_threshold,
                        volume_tier_2_price=ac.volume_tier_2_price,
                        volume_tier_3_threshold=ac.volume_tier_3_threshold,
                        volume_tier_3_price=ac.volume_tier_3_price,
                        minimum_charge=ac.minimum_charge or 0.0,
                        billing_frequency=ac.billing_frequency or "monthly",
                        is_active=ac.is_active or True,
                    )
                    db.add(act_cfg)
                    
            # Create outcome configs if provided
            if billing_model_in.hybrid_outcome_configs:
                for oc in billing_model_in.hybrid_outcome_configs:
                    out_cfg = OutcomeBasedConfig(
                        billing_model_id=model_id,
                        outcome_type=oc.outcome_type,
                        percentage=oc.percentage,
                    )
                    db.add(out_cfg)
        elif new_model_type == "workflow":
            # Create workflow base config
            workflow_cfg = WorkflowBasedConfig(
                billing_model_id=model_id,
                base_platform_fee=billing_model_in.workflow_base_platform_fee or 0.0,
                platform_fee_frequency=billing_model_in.workflow_platform_fee_frequency or "monthly",
                default_billing_frequency=billing_model_in.workflow_default_billing_frequency or "monthly",
                volume_discount_enabled=billing_model_in.workflow_volume_discount_enabled or False,
                volume_discount_threshold=billing_model_in.workflow_volume_discount_threshold,
                volume_discount_percentage=billing_model_in.workflow_volume_discount_percentage,
                overage_multiplier=billing_model_in.workflow_overage_multiplier or 1.0,
                currency=billing_model_in.workflow_currency or "USD",
                is_active=billing_model_in.workflow_is_active or True,
            )
            db.add(workflow_cfg)
            
            # Create workflow types if provided
            if billing_model_in.workflow_types:
                for wt in billing_model_in.workflow_types:
                    workflow_type = WorkflowType(
                        billing_model_id=model_id,
                        workflow_name=wt.workflow_name,
                        workflow_type=wt.workflow_type,
                        description=wt.description,
                        price_per_workflow=wt.price_per_workflow,
                        estimated_compute_cost=wt.estimated_compute_cost or 0.0,
                        estimated_duration_minutes=wt.estimated_duration_minutes,
                        complexity_level=wt.complexity_level or "medium",
                        expected_roi_multiplier=wt.expected_roi_multiplier,
                        business_value_category=wt.business_value_category,
                        volume_tier_1_threshold=wt.volume_tier_1_threshold,
                        volume_tier_1_price=wt.volume_tier_1_price,
                        volume_tier_2_threshold=wt.volume_tier_2_threshold,
                        volume_tier_2_price=wt.volume_tier_2_price,
                        volume_tier_3_threshold=wt.volume_tier_3_threshold,
                        volume_tier_3_price=wt.volume_tier_3_price,
                        billing_frequency=wt.billing_frequency,
                        minimum_charge=wt.minimum_charge or 0.0,
                        is_active=wt.is_active or True,
                    )
                    db.add(workflow_type)
            
            # Create commitment tiers if provided
            if billing_model_in.commitment_tiers:
                for ct in billing_model_in.commitment_tiers:
                    commitment_tier = CommitmentTier(
                        billing_model_id=model_id,
                        tier_name=ct.tier_name,
                        tier_level=ct.tier_level,
                        description=ct.description,
                        minimum_workflows_per_month=ct.minimum_workflows_per_month,
                        minimum_monthly_revenue=ct.minimum_monthly_revenue,
                        included_workflows=ct.included_workflows or 0,
                        included_workflow_types=ct.included_workflow_types,
                        discount_percentage=ct.discount_percentage or 0.0,
                        platform_fee_discount=ct.platform_fee_discount or 0.0,
                        commitment_period_months=ct.commitment_period_months or 12,
                        overage_rate_multiplier=ct.overage_rate_multiplier or 1.0,
                        is_active=ct.is_active or True,
                        is_popular=ct.is_popular or False,
                    )
                    db.add(commitment_tier)
    
    # Update billing model attributes
    for field, value in update_data.items():
        if hasattr(billing_model, field):
            setattr(billing_model, field, value)
    
    # Commit changes to database
    db.commit()
    
    # Re-fetch with eager loading to ensure relationships are available
    updated_billing_model = get_billing_model(db, model_id=model_id)
    if not updated_billing_model:
        raise ValueError("Failed to update billing model")
    
    logger.info(f"Updated billing model: {updated_billing_model.name}")
    return updated_billing_model


def delete_billing_model(db: Session, model_id: int) -> Optional[BillingModel]:
    """
    Delete a billing model
    """
    billing_model = get_billing_model(db, model_id=model_id)
    if not billing_model:
        logger.warning(f"Billing model deletion failed: Model not found with ID {model_id}")
        return None
    
    # Check if billing model is in use by any agents
    if billing_model.agents:
        agent_names = [agent.name for agent in billing_model.agents]
        raise ValueError(
            f"Cannot delete billing model: It is currently in use by agents: {', '.join(agent_names)}"
        )
    
    # Delete billing model from database
    db.delete(billing_model)
    db.commit()
    
    logger.info(f"Deleted billing model: {billing_model.name}")
    return billing_model