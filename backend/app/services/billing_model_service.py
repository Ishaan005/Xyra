"""
Legacy billing model service - delegates to modularized components
This file serves as a compatibility layer for existing API endpoints.
All business logic has been moved to the billing_model module.
"""
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

from app.models.billing_model import BillingModel
from app.schemas.billing_model import BillingModelCreate, BillingModelUpdate
from app.services.billing_model import crud

# Configure logging
logger = logging.getLogger(__name__)


def get_billing_model(db: Session, model_id: int) -> Optional[BillingModel]:
    """
    Get billing model by ID - delegates to modularized CRUD
    """
    try:
        return crud.get_billing_model(db, model_id)
    except ValueError:
        return None


def get_billing_models_by_organization(
    db: Session, org_id: int, skip: int = 0, limit: int = 100
) -> List[BillingModel]:
    """
    Get all billing models for an organization - delegates to modularized CRUD
    """
    return crud.get_billing_models_by_organization(db, org_id, skip, limit)


def create_billing_model(db: Session, billing_model_in: BillingModelCreate) -> BillingModel:
    """
    Create a new billing model - delegates to modularized CRUD
    """
    return crud.create_billing_model(db, billing_model_in)


def update_billing_model(
    db: Session, model_id: int, billing_model_in: BillingModelUpdate
) -> Optional[BillingModel]:
    """
    Update a billing model - delegates to modularized CRUD
    """
    try:
        return crud.update_billing_model(db, model_id, billing_model_in)
    except ValueError:
        return None


def delete_billing_model(db: Session, model_id: int) -> Optional[BillingModel]:
    """
    Delete a billing model - delegates to modularized CRUD
    """
    try:
        return crud.delete_billing_model(db, model_id)
    except ValueError:
        return None