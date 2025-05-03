from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session

from app.models.billing_model import BillingModel
from app.models.organization import Organization
from app.schemas.billing_model import BillingModelCreate, BillingModelUpdate

# Configure logging
logger = logging.getLogger(__name__)


def get_billing_model(db: Session, model_id: int) -> Optional[BillingModel]:
    """
    Get billing model by ID
    """
    return db.query(BillingModel).filter(BillingModel.id == model_id).first()


def get_billing_models_by_organization(
    db: Session, org_id: int, skip: int = 0, limit: int = 100
) -> List[BillingModel]:
    """
    Get all billing models for an organization with pagination
    """
    return (
        db.query(BillingModel)
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
    
    # Validate config based on model type
    validate_billing_config(billing_model_in.model_type, billing_model_in.config)
    
    # Create billing model
    billing_model = BillingModel(
        name=billing_model_in.name,
        description=billing_model_in.description,
        organization_id=billing_model_in.organization_id,
        model_type=billing_model_in.model_type,
        config=billing_model_in.config,
        is_active=billing_model_in.is_active,
    )
    
    # Add billing model to database
    db.add(billing_model)
    db.commit()
    db.refresh(billing_model)

    # Persist config into dedicated tables
    from app.models.billing_model import SeatBasedConfig, ActivityBasedConfig, OutcomeBasedConfig
    cfg = billing_model_in.config
    if billing_model.model_type == "seat":
        seat_cfg = SeatBasedConfig(
            billing_model_id=billing_model.id,
            price_per_seat=cfg.get("price_per_seat", 0),
            billing_frequency=cfg.get("billing_frequency", "monthly"),
        )
        db.add(seat_cfg)
    elif billing_model.model_type == "activity":
        act_cfg = ActivityBasedConfig(
            billing_model_id=billing_model.id,
            price_per_action=cfg.get("price_per_action", 0),
            action_type=cfg.get("action_type", ""),
        )
        db.add(act_cfg)
    elif billing_model.model_type == "outcome":
        out_cfg = OutcomeBasedConfig(
            billing_model_id=billing_model.id,
            outcome_type=cfg.get("outcome_type", ""),
            percentage=cfg.get("percentage", 0),
        )
        db.add(out_cfg)
    elif billing_model.model_type == "hybrid":
        # hybrid may include multiple configs
        if "seat_config" in cfg:
            sc = cfg["seat_config"]
            db.add(SeatBasedConfig(billing_model_id=billing_model.id,
                price_per_seat=sc.get("price_per_seat",0), billing_frequency=sc.get("billing_frequency","monthly")))
        if "activity_config" in cfg:
            for ac in cfg["activity_config"]:
                db.add(ActivityBasedConfig(billing_model_id=billing_model.id,
                    price_per_action=ac.get("price_per_action",0), action_type=ac.get("action_type","")))
        if "outcome_config" in cfg:
            for oc in cfg["outcome_config"]:
                db.add(OutcomeBasedConfig(billing_model_id=billing_model.id,
                    outcome_type=oc.get("outcome_type",""), percentage=oc.get("percentage",0)))
    db.commit()
    
    logger.info(f"Created new billing model: {billing_model.name} for organization {organization.name}")
    return billing_model


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
    
    # Update billing model properties - Using model_dump instead of dict for Pydantic v2
    update_data = billing_model_in.model_dump(exclude_unset=True)
    
    # If config is being updated, validate it
    if "config" in update_data and update_data["config"]:
        model_type = billing_model.model_type
        if "model_type" in update_data:
            model_type = update_data["model_type"]
        validate_billing_config(model_type, update_data["config"])
    
    # If config is being updated, handle child tables
    if "config" in update_data and update_data["config"] is not None:
        from app.models.billing_model import SeatBasedConfig, ActivityBasedConfig, OutcomeBasedConfig
        cfg = update_data["config"]
        # remove old configs for this model_type and recreate
        if billing_model.model_type in ("seat","hybrid"):
            db.query(SeatBasedConfig).filter(SeatBasedConfig.billing_model_id==model_id).delete()
        if billing_model.model_type in ("activity","hybrid"):
            db.query(ActivityBasedConfig).filter(ActivityBasedConfig.billing_model_id==model_id).delete()
        if billing_model.model_type in ("outcome","hybrid"):
            db.query(OutcomeBasedConfig).filter(OutcomeBasedConfig.billing_model_id==model_id).delete()
        db.flush()
        # recreate based on cfg
        if billing_model.model_type == "seat" or billing_model.model_type == "hybrid" and "seat_config" not in cfg:
            sc = cfg.get("seat_config", cfg)
            db.add(SeatBasedConfig(billing_model_id=model_id,
                price_per_seat=sc.get("price_per_seat",0), billing_frequency=sc.get("billing_frequency","monthly")))
        if billing_model.model_type == "activity" or billing_model.model_type == "hybrid":
            acts = cfg.get("activity_config", [cfg]) if billing_model.model_type=="activity" else cfg.get("activity_config", [])
            for acfg in acts:
                db.add(ActivityBasedConfig(billing_model_id=model_id,
                    price_per_action=acfg.get("price_per_action",0), action_type=acfg.get("action_type","")))
        if billing_model.model_type == "outcome" or billing_model.model_type == "hybrid":
            outs = cfg.get("outcome_config", [cfg]) if billing_model.model_type=="outcome" else cfg.get("outcome_config", [])
            for ocfg in outs:
                db.add(OutcomeBasedConfig(billing_model_id=model_id,
                    outcome_type=ocfg.get("outcome_type",""), percentage=ocfg.get("percentage",0)))
    
    # Update billing model attributes
    for field, value in update_data.items():
        if hasattr(billing_model, field):
            setattr(billing_model, field, value)
    
    # Commit changes to database
    db.commit()
    db.refresh(billing_model)
    
    logger.info(f"Updated billing model: {billing_model.name}")
    return billing_model


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


def validate_billing_config(model_type: str, config: Dict[str, Any]) -> None:
    """
    Validate billing model configuration based on model type
    """
    if model_type == "seat":
        if "price_per_seat" not in config:
            raise ValueError("Seat-based billing model must include 'price_per_seat' in config")
        
        if not isinstance(config["price_per_seat"], (int, float)) or config["price_per_seat"] <= 0:
            raise ValueError("'price_per_seat' must be a positive number")
        
        if "billing_frequency" in config and config["billing_frequency"] not in ["monthly", "quarterly", "yearly"]:
            raise ValueError("'billing_frequency' must be one of: monthly, quarterly, yearly")
    
    elif model_type == "activity":
        if "price_per_action" not in config:
            raise ValueError("Activity-based billing model must include 'price_per_action' in config")
        
        if not isinstance(config["price_per_action"], (int, float)) or config["price_per_action"] <= 0:
            raise ValueError("'price_per_action' must be a positive number")
        
        if "action_type" not in config:
            raise ValueError("Activity-based billing model must include 'action_type' in config")
    
    elif model_type == "outcome":
        if "outcome_type" not in config:
            raise ValueError("Outcome-based billing model must include 'outcome_type' in config")
        
        if "percentage" not in config:
            raise ValueError("Outcome-based billing model must include 'percentage' in config")
        
        if not isinstance(config["percentage"], (int, float)) or config["percentage"] <= 0:
            raise ValueError("'percentage' must be a positive number")
    
    elif model_type == "hybrid":
        # Hybrid can have a mix of the above configurations
        if "base_fee" in config and (not isinstance(config["base_fee"], (int, float)) or config["base_fee"] < 0):
            raise ValueError("'base_fee' must be a non-negative number")
        
        # Must have at least one billing component
        if not any(key in config for key in ["seat_config", "activity_config", "outcome_config", "base_fee"]):
            raise ValueError("Hybrid billing model must include at least one billing component")
        
        # Validate each component if present
        if "seat_config" in config and config["seat_config"]:
            if "price_per_seat" not in config["seat_config"]:
                raise ValueError("Seat configuration must include 'price_per_seat'")
        
        if "activity_config" in config and config["activity_config"]:
            if not isinstance(config["activity_config"], list):
                raise ValueError("'activity_config' must be a list of activity configurations")
            
            for activity in config["activity_config"]:
                if "price_per_action" not in activity or "action_type" not in activity:
                    raise ValueError("Each activity configuration must include 'price_per_action' and 'action_type'")
        
        if "outcome_config" in config and config["outcome_config"]:
            if not isinstance(config["outcome_config"], list):
                raise ValueError("'outcome_config' must be a list of outcome configurations")
            
            for outcome in config["outcome_config"]:
                if "outcome_type" not in outcome or "percentage" not in outcome:
                    raise ValueError("Each outcome configuration must include 'outcome_type' and 'percentage'")


def calculate_cost(billing_model: BillingModel, usage_data: Dict[str, Any]) -> float:
    """
    Calculate cost based on billing model and usage data using dedicated config tables
    """
    # Use dedicated config tables via relationships
    total_cost = 0.0
    if billing_model.model_type == "seat":
        # Expect one SeatBasedConfig row
        if billing_model.seat_config:
            cfg = billing_model.seat_config[0]
            seats = usage_data.get("seats", 0)
            total_cost = cfg.price_per_seat * seats
    elif billing_model.model_type == "activity":
        # Expect one or more ActivityBasedConfig rows
        actions = usage_data.get("actions", 0)
        # if multiple action_types, sum matching
        for cfg in billing_model.activity_config:
            total_cost += cfg.price_per_action * actions
    elif billing_model.model_type == "outcome":
        # Outcome-based billing: percentage of outcome_value
        outcome_value = usage_data.get("outcome_value", 0)
        for cfg in billing_model.outcome_config:
            total_cost += (cfg.percentage / 100.0) * outcome_value
    elif billing_model.model_type == "hybrid":
        # Hybrid: base fee from JSON stored, plus each component
        # Base fee fallback to JSON
        total_cost += billing_model.config.get("base_fee", 0)
        # Seat
        if hasattr(billing_model, "seat_config") and billing_model.seat_config:
            seats = usage_data.get("seats", 0)
            cfg = billing_model.seat_config[0]
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