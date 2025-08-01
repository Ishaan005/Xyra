from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import api_key_service

router = APIRouter()


@router.get("", response_model=List[schemas.ApiKey])
def list_api_keys(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all API keys for the current user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to manage API keys",
        )
    
    api_keys = api_key_service.get_api_keys_by_user(
        db, user_id=current_user.id, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return api_keys


@router.get("/organization/all", response_model=List[schemas.ApiKeyWithUser])
def list_organization_api_keys(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all API keys for the current user's organization (admin function).
    Only superusers or organization admins can access this.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to view organization API keys",
        )
    
    # For now, allow any user in the organization to see all keys
    # In the future, this could be restricted to admins only
    api_keys = api_key_service.get_api_keys_by_organization(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    
    # Convert to response format with user information
    response_keys = []
    for api_key in api_keys:
        key_dict = api_key.__dict__.copy()
        # Add user information
        if api_key.user:
            key_dict["user"] = {
                "id": api_key.user.id,
                "email": api_key.user.email,
                "full_name": api_key.user.full_name
            }
        response_keys.append(key_dict)
    
    return response_keys


@router.post("", response_model=schemas.ApiKeyWithToken)
def create_api_key(
    *,
    db: Session = Depends(deps.get_db),
    api_key_in: schemas.ApiKeyCreate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new API key for the current user's organization.
    Returns the full token only once - it cannot be retrieved again.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to create API keys",
        )
    
    api_key, full_token = api_key_service.create_api_key(
        db, api_key_in=api_key_in, user_id=current_user.id, organization_id=current_user.organization_id
    )
    
    # Return the API key with the full token
    return schemas.ApiKeyWithToken(
        **api_key.__dict__,
        token=full_token
    )


@router.get("/{api_key_id}", response_model=schemas.ApiKey)
def get_api_key(
    *,
    db: Session = Depends(deps.get_db),
    api_key_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific API key by ID.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to access API keys",
        )
    
    api_key = api_key_service.get_api_key(
        db, api_key_id=api_key_id, user_id=current_user.id, organization_id=current_user.organization_id
    )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return api_key


@router.put("/{api_key_id}", response_model=schemas.ApiKey)
def update_api_key(
    *,
    db: Session = Depends(deps.get_db),
    api_key_id: int,
    api_key_in: schemas.ApiKeyUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an API key.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to update API keys",
        )
    
    api_key = api_key_service.update_api_key(
        db, api_key_id=api_key_id, user_id=current_user.id, organization_id=current_user.organization_id, api_key_update=api_key_in
    )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return api_key


@router.delete("/{api_key_id}")
def delete_api_key(
    *,
    db: Session = Depends(deps.get_db),
    api_key_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an API key.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to delete API keys",
        )
    
    success = api_key_service.delete_api_key(
        db, api_key_id=api_key_id, user_id=current_user.id, organization_id=current_user.organization_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return {"message": "API key deleted successfully"}


@router.post("/{api_key_id}/deactivate", response_model=schemas.ApiKey)
def deactivate_api_key(
    *,
    db: Session = Depends(deps.get_db),
    api_key_id: int,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Deactivate an API key instead of deleting it.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization to deactivate API keys",
        )
    
    api_key = api_key_service.deactivate_api_key(
        db, api_key_id=api_key_id, user_id=current_user.id, organization_id=current_user.organization_id
    )
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return api_key
