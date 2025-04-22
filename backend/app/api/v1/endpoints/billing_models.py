from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import billing_model_service, organization_service

router = APIRouter()


@router.get("/", response_model=List[schemas.BillingModel])
def read_billing_models(
    org_id: Optional[int] = Query(None, description="Organization ID to filter billing models"),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve billing models for an organization.
    
    Users can only access billing models for their own organization unless they are superusers.
    """
    # Determine target org_id: use query param or default to user's org
    if org_id is None:
        org_id = current_user.organization_id
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access billing models for this organization",
        )
    
    # Check if organization exists
    organization = organization_service.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    # Get billing models for the organization
    billing_models = billing_model_service.get_billing_models_by_organization(
        db, org_id=org_id, skip=skip, limit=limit
    )
    
    return billing_models


@router.post("/", response_model=schemas.BillingModel)
def create_billing_model(
    *,
    db: Session = Depends(deps.get_db),
    billing_model_in: schemas.BillingModelCreate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new billing model for an organization.
    
    Users can only create billing models for their own organization unless they are superusers.
    """
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != billing_model_in.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create billing models for this organization",
        )
    
    # Create billing model
    try:
        billing_model = billing_model_service.create_billing_model(db, billing_model_in=billing_model_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return billing_model


@router.get("/{model_id}", response_model=schemas.BillingModel)
def read_billing_model(
    model_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific billing model by ID.
    
    Users can only access billing models for their own organization unless they are superusers.
    """
    # Get billing model
    billing_model = billing_model_service.get_billing_model(db, model_id=model_id)
    if not billing_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing model not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != billing_model.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this billing model",
        )
    
    return billing_model


@router.put("/{model_id}", response_model=schemas.BillingModel)
def update_billing_model(
    *,
    db: Session = Depends(deps.get_db),
    model_id: int,
    billing_model_in: schemas.BillingModelUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a billing model.
    
    Users can only update billing models for their own organization unless they are superusers.
    """
    # Get billing model
    billing_model = billing_model_service.get_billing_model(db, model_id=model_id)
    if not billing_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing model not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != billing_model.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this billing model",
        )
    
    # Update billing model
    try:
        updated_billing_model = billing_model_service.update_billing_model(
            db, model_id=model_id, billing_model_in=billing_model_in
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return updated_billing_model


@router.delete("/{model_id}", response_model=schemas.BillingModel)
def delete_billing_model(
    *,
    db: Session = Depends(deps.get_db),
    model_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a billing model.
    
    Users can only delete billing models for their own organization unless they are superusers.
    Cannot delete billing models that are in use by agents.
    """
    # Get billing model
    billing_model = billing_model_service.get_billing_model(db, model_id=model_id)
    if not billing_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing model not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != billing_model.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this billing model",
        )
    
    # Delete billing model
    try:
        billing_model = billing_model_service.delete_billing_model(db, model_id=model_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return billing_model


@router.post("/{model_id}/calculate", response_model=dict)
def calculate_billing_cost(
    *,
    db: Session = Depends(deps.get_db),
    model_id: int,
    usage_data: dict,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calculate cost for a billing model based on usage data.
    
    Returns the calculated cost based on the billing model configuration and provided usage data.
    """
    # Get billing model
    billing_model = billing_model_service.get_billing_model(db, model_id=model_id)
    if not billing_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing model not found",
        )
    
    # Check permissions
    if not current_user.is_superuser and (not current_user.organization_id or current_user.organization_id != billing_model.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this billing model",
        )
    
    # Calculate cost
    try:
        cost = billing_model_service.calculate_cost(billing_model, usage_data)
        return {
            "cost": cost,
            "currency": "USD",  # Default currency
            "billing_model_id": model_id,
            "billing_model_type": billing_model.model_type,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error calculating cost: {str(e)}",
        )