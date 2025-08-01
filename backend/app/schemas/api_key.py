from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ApiKeyBase(BaseModel):
    """Base API key schema"""
    name: str
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class ApiKeyCreate(ApiKeyBase):
    """Schema for creating API keys"""
    pass


class ApiKeyUpdate(BaseModel):
    """Schema for updating API keys"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class ApiKeyInDB(ApiKeyBase):
    """Schema for API keys in database"""
    id: int
    user_id: int
    organization_id: int
    key_prefix: str
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApiKey(ApiKeyInDB):
    """Schema for API key responses (without sensitive data)"""
    pass


class ApiKeyWithUser(ApiKeyInDB):
    """Schema for API key responses with user information (for organization listings)"""
    user: Optional[dict] = None  # Will contain user info when needed


class ApiKeyWithToken(ApiKeyInDB):
    """Schema for API key creation response (includes the full token)"""
    token: str
