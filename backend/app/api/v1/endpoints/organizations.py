from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import organization_service

router = APIRouter()


@router.get("", response_model=List[schemas.Organization])
def read_organizations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve organizations.
    Regular users can only see their own organization.
    Superusers can see all organizations.
    """
    if current_user.is_superuser:
        organizations = organization_service.get_organizations(db, skip=skip, limit=limit)
    elif current_user.organization_id:
        organization = organization_service.get_organization(db, org_id=current_user.organization_id)
        organizations = [organization] if organization else []
    else:
        organizations = []
    return organizations


@router.post("", response_model=schemas.Organization)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_in: schemas.OrganizationCreate,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Create new organization.
    Only superusers can create organizations.
    """
    organization = organization_service.get_organization_by_name(db, name=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this name already exists",
        )
    organization = organization_service.create_organization(db, org_in=organization_in)
    return organization


@router.get("/{organization_id}", response_model=schemas.Organization)
def read_organization(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific organization by ID.
    Regular users can only see their own organization.
    Superusers can see any organization.
    """
    organization = organization_service.get_organization(db, org_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    if (not current_user.is_superuser and 
        (not current_user.organization_id or current_user.organization_id != organization_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return organization


@router.put("/{organization_id}", response_model=schemas.Organization)
def update_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: int,
    organization_in: schemas.OrganizationUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update organization.
    Regular users can only update their own organization if they are admins.
    Superusers can update any organization.
    """
    organization = organization_service.get_organization(db, org_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    if (not current_user.is_superuser and 
        (not current_user.organization_id or current_user.organization_id != organization_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    organization = organization_service.update_organization(
        db, org_id=organization_id, org_in=organization_in
    )
    return organization


@router.delete("/{organization_id}", response_model=schemas.Organization)
def delete_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: int,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Delete organization.
    Only superusers can delete organizations.
    """
    organization = organization_service.get_organization(db, org_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    organization = organization_service.delete_organization(db, org_id=organization_id)
    return organization


@router.get("/{organization_id}/stats", response_model=schemas.OrganizationWithStats)
def get_organization_stats(
    organization_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization statistics including agent counts, costs, and revenues.
    """
    organization = organization_service.get_organization(db, org_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    if (not current_user.is_superuser and 
        (not current_user.organization_id or current_user.organization_id != organization_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get organization stats
    stats = organization_service.get_organization_stats(db, org_id=organization_id)
    
    # Combine organization data with stats - Updated to use model_dump for Pydantic v2 compatibility
    org_dict = organization.__dict__.copy() if hasattr(organization, "__dict__") else {}
    org_data = {
        **org_dict,
        **stats
    }
    
    return org_data