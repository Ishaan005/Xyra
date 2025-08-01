import secrets
import hashlib
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyUpdate


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key with format: xyra_<32-char-random>
    Returns: (full_key, key_hash, key_prefix)
    """
    # Generate random key
    random_part = secrets.token_urlsafe(24)  # 32 chars after encoding
    full_key = f"xyra_{random_part}"
    
    # Create hash for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Create prefix for display (first 12 chars + ...)
    key_prefix = full_key[:12] + "..."
    
    return full_key, key_hash, key_prefix


def create_api_key(db: Session, api_key_in: ApiKeyCreate, user_id: int, organization_id: int) -> tuple[ApiKey, str]:
    """Create a new API key for a user in an organization"""
    full_key, key_hash, key_prefix = generate_api_key()
    
    api_key = ApiKey(
        user_id=user_id,
        organization_id=organization_id,
        name=api_key_in.name,
        description=api_key_in.description,
        key_hash=key_hash,
        key_prefix=key_prefix,
        expires_at=api_key_in.expires_at,
        is_active=True
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return api_key, full_key


def get_api_keys_by_user(db: Session, user_id: int, organization_id: int, skip: int = 0, limit: int = 100) -> List[ApiKey]:
    """Get all API keys for a user's organization"""
    return db.query(ApiKey).filter(
        and_(ApiKey.organization_id == organization_id, ApiKey.user_id == user_id)
    ).offset(skip).limit(limit).all()


def get_api_keys_by_organization(db: Session, organization_id: int, skip: int = 0, limit: int = 100) -> List[ApiKey]:
    """Get all API keys for an organization (admin function)"""
    return db.query(ApiKey).filter(
        ApiKey.organization_id == organization_id
    ).offset(skip).limit(limit).all()


def get_api_key(db: Session, api_key_id: int, user_id: int, organization_id: int) -> Optional[ApiKey]:
    """Get a specific API key by ID (user must own it and it must be in their org)"""
    return db.query(ApiKey).filter(
        and_(
            ApiKey.id == api_key_id, 
            ApiKey.user_id == user_id,
            ApiKey.organization_id == organization_id
        )
    ).first()


def get_api_key_by_hash(db: Session, key_hash: str) -> Optional[ApiKey]:
    """Get API key by hash (for authentication)"""
    return db.query(ApiKey).filter(
        and_(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    ).first()


def authenticate_api_key(db: Session, api_key: str) -> Optional[ApiKey]:
    """Authenticate an API key and return the associated key object"""
    if not api_key.startswith("xyra_"):
        return None
    
    # Hash the provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Find the key in database
    api_key_obj = get_api_key_by_hash(db, key_hash)
    
    if api_key_obj:
        # Check if key is expired (use getattr to get actual value)
        expires_at = getattr(api_key_obj, 'expires_at')
        if expires_at is not None and expires_at < datetime.now(timezone.utc):
            return None
        
        # Update last used timestamp
        setattr(api_key_obj, 'last_used', datetime.now(timezone.utc))
        db.commit()
        
    return api_key_obj


def update_api_key(db: Session, api_key_id: int, user_id: int, organization_id: int, api_key_update: ApiKeyUpdate) -> Optional[ApiKey]:
    """Update an API key"""
    api_key = get_api_key(db, api_key_id, user_id, organization_id)
    if not api_key:
        return None
    
    update_data = api_key_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(api_key, field, value)
    
    db.commit()
    db.refresh(api_key)
    return api_key


def delete_api_key(db: Session, api_key_id: int, user_id: int, organization_id: int) -> bool:
    """Delete an API key"""
    api_key = get_api_key(db, api_key_id, user_id, organization_id)
    if not api_key:
        return False
    
    db.delete(api_key)
    db.commit()
    return True


def deactivate_api_key(db: Session, api_key_id: int, user_id: int, organization_id: int) -> Optional[ApiKey]:
    """Deactivate an API key instead of deleting it"""
    api_key = get_api_key(db, api_key_id, user_id, organization_id)
    if not api_key:
        return None
    
    setattr(api_key, 'is_active', False)
    db.commit()
    db.refresh(api_key)
    return api_key
