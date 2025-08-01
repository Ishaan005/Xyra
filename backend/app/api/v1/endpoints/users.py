from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import user_service

router = APIRouter()


@router.get("", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    Regular users can only see their own user.
    Superusers can see all users.
    """
    if bool(current_user.is_superuser):
        users = user_service.get_users(db, skip=skip, limit=limit)
    else:
        users = [current_user]
    return users


@router.post("", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Create new user.
    Only superusers can create new users.
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    user = user_service.create_user(db, user_in=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    Regular users can only see their own user.
    Superusers can see any user.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if getattr(user, 'id') != getattr(current_user, 'id') and not bool(current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    Regular users can only update their own user.
    Superusers can update any user.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if getattr(user, 'id') != getattr(current_user, 'id') and not bool(current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    user = user_service.update_user(db, user_id=user_id, user_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: schemas.User = Depends(deps.get_current_superuser),
) -> Any:
    """
    Delete a user.
    Only superusers can delete users.
    """
    user = user_service.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user = user_service.delete_user(db, user_id=user_id)
    return user