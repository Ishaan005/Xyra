from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session, joinedload

from app.models.billing_model import BillingModel
from app.models.organization import Organization
from app.schemas.billing_model import BillingModelCreate, BillingModelUpdate

# Configure logging
logger = logging.getLogger(__name__)


def get_billing_model(db: Session, model_id: int) -> Optional[BillingModel]:
    """
    Get billing model by ID with eagerly loaded relationships
    """
    return (
        db.query(BillingModel)
        .options(
            joinedload(BillingModel.seat_config),
            joinedload(BillingModel.activity_config),
            joinedload(BillingModel.outcome_config),
            joinedload(BillingModel.hybrid_config)
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
            joinedload(BillingModel.seat_config),
            joinedload(BillingModel.activity_config),
            joinedload(BillingModel.outcome_config),
            joinedload(BillingModel.hybrid_config)
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
    valid_types = ["seat", "activity", "outcome", "hybrid"]
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
    from app.models.billing_model import SeatBasedConfig, ActivityBasedConfig, OutcomeBasedConfig, HybridConfig
    
    if billing_model_in.model_type == "seat":
        seat_cfg = SeatBasedConfig(
            billing_model_id=billing_model.id,
            price_per_seat=billing_model_in.seat_price_per_seat,
            billing_frequency=billing_model_in.seat_billing_frequency,
        )
        db.add(seat_cfg)
    elif billing_model_in.model_type == "activity":
        act_cfg = ActivityBasedConfig(
            billing_model_id=billing_model.id,
            price_per_action=billing_model_in.activity_price_per_action,
            action_type=billing_model_in.activity_action_type,
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
        
        # Create seat config if provided
        if billing_model_in.hybrid_seat_config:
            seat_cfg = SeatBasedConfig(
                billing_model_id=billing_model.id,
                price_per_seat=billing_model_in.hybrid_seat_config.price_per_seat,
                billing_frequency=billing_model_in.hybrid_seat_config.billing_frequency,
            )
            db.add(seat_cfg)
            
        # Create activity configs if provided
        if billing_model_in.hybrid_activity_configs:
            for ac in billing_model_in.hybrid_activity_configs:
                act_cfg = ActivityBasedConfig(
                    billing_model_id=billing_model.id,
                    price_per_action=ac.price_per_action,
                    action_type=ac.action_type,
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
        valid_types = ["seat", "activity", "outcome", "hybrid"]
        if update_data["model_type"] not in valid_types:
            raise ValueError(
                f"Invalid billing model type: {update_data['model_type']}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
    
    # Validate config based on model type and input fields if config fields are being updated
    if any(field in update_data for field in [
        "seat_price_per_seat", "seat_billing_frequency",
        "activity_price_per_action", "activity_action_type", 
        "outcome_outcome_type", "outcome_percentage",
        "hybrid_base_fee", "hybrid_seat_config", "hybrid_activity_configs", "hybrid_outcome_configs"
    ]):
        current_model_type = str(billing_model.model_type)
        validate_billing_config_from_schema(billing_model_in, current_model_type)
    
    # Handle config updates through dedicated schema fields
    config_updated = any(field in update_data for field in [
        "seat_price_per_seat", "seat_billing_frequency",
        "activity_price_per_action", "activity_action_type", 
        "outcome_outcome_type", "outcome_percentage",
        "hybrid_base_fee", "hybrid_seat_config", "hybrid_activity_configs", "hybrid_outcome_configs"
    ])
    
    if config_updated:
        from app.models.billing_model import SeatBasedConfig, ActivityBasedConfig, OutcomeBasedConfig, HybridConfig
        
        # Get the current model type as a string value
        current_model_type = str(billing_model.model_type)
        model_type_changing = "model_type" in update_data
        new_model_type = update_data.get("model_type", current_model_type)

        # Remove old configs for this model_type and recreate
        if current_model_type in ("seat", "hybrid") or model_type_changing:
            db.query(SeatBasedConfig).filter(SeatBasedConfig.billing_model_id == model_id).delete()
        if current_model_type in ("activity", "hybrid") or model_type_changing:
            db.query(ActivityBasedConfig).filter(ActivityBasedConfig.billing_model_id == model_id).delete()
        if current_model_type in ("outcome", "hybrid") or model_type_changing:
            db.query(OutcomeBasedConfig).filter(OutcomeBasedConfig.billing_model_id == model_id).delete()
        if current_model_type == "hybrid" or model_type_changing:
            db.query(HybridConfig).filter(HybridConfig.billing_model_id == model_id).delete()
        db.flush()
        
        # Recreate configs based on new values and model type
        if new_model_type == "seat":
            if billing_model_in.seat_price_per_seat is not None:
                seat_cfg = SeatBasedConfig(
                    billing_model_id=model_id,
                    price_per_seat=billing_model_in.seat_price_per_seat,
                    billing_frequency=billing_model_in.seat_billing_frequency or "monthly",
                )
                db.add(seat_cfg)
        elif new_model_type == "activity":
            if billing_model_in.activity_price_per_action is not None:
                act_cfg = ActivityBasedConfig(
                    billing_model_id=model_id,
                    price_per_action=billing_model_in.activity_price_per_action,
                    action_type=billing_model_in.activity_action_type,
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
            
            # Create seat config if provided
            if billing_model_in.hybrid_seat_config:
                seat_cfg = SeatBasedConfig(
                    billing_model_id=model_id,
                    price_per_seat=billing_model_in.hybrid_seat_config.price_per_seat,
                    billing_frequency=billing_model_in.hybrid_seat_config.billing_frequency,
                )
                db.add(seat_cfg)
                
            # Create activity configs if provided
            if billing_model_in.hybrid_activity_configs:
                for ac in billing_model_in.hybrid_activity_configs:
                    act_cfg = ActivityBasedConfig(
                        billing_model_id=model_id,
                        price_per_action=ac.price_per_action,
                        action_type=ac.action_type,
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
    
    if model_type == "seat":
        if billing_model_in.seat_price_per_seat is None or billing_model_in.seat_price_per_seat <= 0:
            raise ValueError("Seat-based billing model must include a positive 'seat_price_per_seat'")
        
        if billing_model_in.seat_billing_frequency and billing_model_in.seat_billing_frequency not in ["monthly", "quarterly", "yearly"]:
            raise ValueError("'seat_billing_frequency' must be one of: monthly, quarterly, yearly")
        
    elif model_type == "activity":
        if billing_model_in.activity_price_per_action is None or billing_model_in.activity_price_per_action <= 0:
            raise ValueError("Activity-based billing model must include a positive 'activity_price_per_action'")
        
        if not billing_model_in.activity_action_type:
            raise ValueError("Activity-based billing model must include 'activity_action_type'")
    
    elif model_type == "outcome":
        if not billing_model_in.outcome_outcome_type:
            raise ValueError("Outcome-based billing model must include 'outcome_outcome_type'")
        
        if billing_model_in.outcome_percentage is None or billing_model_in.outcome_percentage <= 0:
            raise ValueError("Outcome-based billing model must include a positive 'outcome_percentage'")
    
    elif model_type == "hybrid":
        # Hybrid must have at least one billing component
        has_base_fee = billing_model_in.hybrid_base_fee is not None and billing_model_in.hybrid_base_fee >= 0
        has_seat = billing_model_in.hybrid_seat_config is not None
        has_activity = billing_model_in.hybrid_activity_configs is not None and len(billing_model_in.hybrid_activity_configs) > 0
        has_outcome = billing_model_in.hybrid_outcome_configs is not None and len(billing_model_in.hybrid_outcome_configs) > 0
        
        if not any([has_base_fee, has_seat, has_activity, has_outcome]):
            raise ValueError("Hybrid billing model must include at least one billing component")
        
        # Validate each component if present
        if has_seat:
            if billing_model_in.hybrid_seat_config.price_per_seat <= 0:
                raise ValueError("Seat configuration must include a positive 'price_per_seat'")
        
        if has_activity:
            for activity in billing_model_in.hybrid_activity_configs:
                if activity.price_per_action <= 0 or not activity.action_type:
                    raise ValueError("Each activity configuration must include positive 'price_per_action' and 'action_type'")
        
        if has_outcome:
            for outcome in billing_model_in.hybrid_outcome_configs:
                if not outcome.outcome_type or outcome.percentage <= 0:
                    raise ValueError("Each outcome configuration must include 'outcome_type' and positive 'percentage'")


def calculate_cost(billing_model: BillingModel, usage_data: Dict[str, Any]) -> float:
    """
    Calculate cost based on billing model and usage data using dedicated config tables
    """
    # Use dedicated config tables via relationships
    total_cost = 0.0
    current_model_type = str(billing_model.model_type)
    
    if current_model_type == "seat":
        # Expect one SeatBasedConfig row
        if billing_model.seat_config:
            cfg = billing_model.seat_config
            seats = usage_data.get("seats", 0)
            total_cost = cfg.price_per_seat * seats
    elif current_model_type == "activity":
        # Expect one or more ActivityBasedConfig rows
        actions = usage_data.get("actions", 0)
        # if multiple action_types, sum matching
        for cfg in billing_model.activity_config:
            total_cost += cfg.price_per_action * actions
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
        # Seat
        if hasattr(billing_model, "seat_config") and billing_model.seat_config:
            seats = usage_data.get("seats", 0)
            cfg = billing_model.seat_config
            total_cost += cfg.price_per_seat * seats
        # Activity
        activities = usage_data.get("actions", 0)
        for cfg in billing_model.activity_config:
            total_cost += cfg.price_per_action * activities
        # Outcome
        outcome_value = usage_data.get("outcome_value", 0)
        for cfg in billing_model.outcome_config:
            total_cost += (cfg.percentage / 100.0) * outcome_value
    return total_cost