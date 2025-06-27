from typing import List
from sqlalchemy.orm import Session, joinedload
from app.models.billing_model import BillingModel
from app.models.organization import Organization
from app.schemas.billing_model import BillingModelCreate, BillingModelUpdate
from .validation import validate_billing_config_from_schema
from .config import (
    create_agent_config, create_activity_config, create_outcome_config, create_hybrid_config, create_workflow_config, delete_all_configs
)
import logging

logger = logging.getLogger(__name__)

# --- Centralized config field lists ---
CONFIG_FIELDS = [
    # Agent
    "agent_base_agent_fee", "agent_billing_frequency", "agent_setup_fee", "agent_volume_discount_enabled", "agent_volume_discount_threshold", "agent_volume_discount_percentage", "agent_tier",
    # Activity
    "activity_price_per_unit", "activity_activity_type", "activity_unit_type", "activity_base_agent_fee", "activity_volume_pricing_enabled", "activity_volume_tier_1_threshold", "activity_volume_tier_1_price", "activity_volume_tier_2_threshold", "activity_volume_tier_2_price", "activity_volume_tier_3_threshold", "activity_volume_tier_3_price", "activity_minimum_charge", "activity_billing_frequency", "activity_is_active",
    # Outcome
    "outcome_outcome_type", "outcome_percentage",
    # Hybrid
    "hybrid_base_fee", "hybrid_agent_config", "hybrid_activity_configs", "hybrid_outcome_configs",
    # Workflow
    "workflow_base_platform_fee", "workflow_platform_fee_frequency", "workflow_default_billing_frequency", "workflow_volume_discount_enabled", "workflow_volume_discount_threshold", "workflow_volume_discount_percentage", "workflow_overage_multiplier", "workflow_currency", "workflow_is_active", "workflow_types", "commitment_tiers"
]

# --- CRUD functions ---
def get_billing_model(db: Session, model_id: int) -> BillingModel:
    """
    Get billing model by ID with eagerly loaded relationships
    """
    model = (
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
    if not model:
        raise ValueError(f"Billing model with ID {model_id} not found")
    return model

def get_billing_models_by_organization(db: Session, org_id: int, skip: int = 0, limit: int = 100) -> List[BillingModel]:
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
    organization = db.query(Organization).filter(Organization.id == billing_model_in.organization_id).first()
    if not organization:
        raise ValueError(f"Organization with ID {billing_model_in.organization_id} not found")
    valid_types = ["agent", "activity", "outcome", "hybrid", "workflow"]
    if billing_model_in.model_type not in valid_types:
        raise ValueError(
            f"Invalid billing model type: {billing_model_in.model_type}. "
            f"Must be one of: {', '.join(valid_types)}"
        )
    validate_billing_config_from_schema(billing_model_in)
    billing_model = BillingModel(
        name=billing_model_in.name,
        description=billing_model_in.description,
        organization_id=billing_model_in.organization_id,
        model_type=billing_model_in.model_type,
        is_active=billing_model_in.is_active,
    )
    db.add(billing_model)
    db.commit()
    db.refresh(billing_model)
    # Ensure we get the actual integer value for the primary key
    model_id_val = getattr(billing_model, 'id', None)
    if not isinstance(model_id_val, int):
        model_id_val = billing_model.__dict__.get('id')
    if not isinstance(model_id_val, int):
        raise ValueError("Could not determine integer ID for created billing model.")
    config_creators = {
        "agent": create_agent_config,
        "activity": create_activity_config,
        "outcome": create_outcome_config,
        "hybrid": create_hybrid_config,
        "workflow": create_workflow_config,
    }
    config_creator = config_creators.get(billing_model_in.model_type)
    if config_creator:
        config_creator(db, billing_model, billing_model_in)
    db.commit()
    created_billing_model = get_billing_model(db, model_id=model_id_val)
    logger.info(f"Created new billing model: {created_billing_model.name} for organization {organization.name}")
    return created_billing_model

def update_billing_model(db: Session, model_id: int, billing_model_in: BillingModelUpdate) -> BillingModel:
    """
    Update a billing model
    """
    billing_model = get_billing_model(db, model_id=model_id)
    update_data = billing_model_in.model_dump(exclude_unset=True)
    if "model_type" in update_data:
        valid_types = ["agent", "activity", "outcome", "hybrid", "workflow"]
        if update_data["model_type"] not in valid_types:
            raise ValueError(
                f"Invalid billing model type: {update_data['model_type']}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
    if any(field in update_data for field in CONFIG_FIELDS):
        current_model_type = str(billing_model.model_type)
        validate_billing_config_from_schema(billing_model_in, current_model_type)
        model_type_changing = "model_type" in update_data
        new_model_type = update_data.get("model_type", current_model_type)
        delete_all_configs(db, model_id, current_model_type, model_type_changing)
        config_creators = {
            "agent": create_agent_config,
            "activity": create_activity_config,
            "outcome": create_outcome_config,
            "hybrid": create_hybrid_config,
            "workflow": create_workflow_config,
        }
        config_creator = config_creators.get(new_model_type)
        if config_creator:
            config_creator(db, billing_model, billing_model_in)
    for field, value in update_data.items():
        if hasattr(billing_model, field):
            setattr(billing_model, field, value)
    db.commit()
    updated_billing_model = get_billing_model(db, model_id=model_id)
    logger.info(f"Updated billing model: {updated_billing_model.name}")
    return updated_billing_model

def delete_billing_model(db: Session, model_id: int) -> BillingModel:
    """
    Delete a billing model
    """
    billing_model = get_billing_model(db, model_id=model_id)
    if billing_model.agents:
        raise ValueError("Cannot delete billing model that is in use by agents")
    db.delete(billing_model)
    db.commit()
    logger.info(f"Deleted billing model: {billing_model.name}")
    return billing_model
