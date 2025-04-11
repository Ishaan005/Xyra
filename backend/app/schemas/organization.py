from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating organizations"""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating organizations"""
    name: Optional[str] = None
    description: Optional[str] = None


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