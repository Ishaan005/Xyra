from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str
    description: Optional[str] = None
    # New fields from revised schema
    external_id: Optional[str] = None
    status: str = 'active'
    billing_email: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    timezone: str = 'UTC'
    settings: Dict = {}


class OrganizationCreate(OrganizationBase):
    """Schema for creating organizations"""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating organizations"""
    name: Optional[str] = None
    description: Optional[str] = None
    external_id: Optional[str] = None
    status: Optional[str] = None
    billing_email: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    timezone: Optional[str] = None
    settings: Optional[Dict] = None


class OrganizationInDBBase(OrganizationBase):
    """Base schema for organizations in DB"""
    id: int
    created_at: datetime
    updated_at: datetime
    stripe_customer_id: Optional[str] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class Organization(OrganizationInDBBase):
    """Schema for organization responses"""
    pass


class OrganizationWithStats(Organization):
    """Organization with usage statistics"""
    agent_count: int
    active_agent_count: int
    monthly_cost: float
    monthly_revenue: float