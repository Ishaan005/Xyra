from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class BillingModelBase(BaseModel):
    """Base billing model schema"""
    name: str
    description: Optional[str] = None
    model_type: str = Field(..., description="One of: 'seat', 'activity', 'outcome', 'hybrid'")
    config: Dict[str, Any] = {}
    is_active: bool = True


class BillingModelCreate(BillingModelBase):
    """Schema for creating billing models"""
    organization_id: int


class BillingModelUpdate(BaseModel):
    """Schema for updating billing models"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class BillingModelInDBBase(BillingModelBase):
    """Base schema for billing models in DB"""
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    # Nested config from dedicated tables
    seat_config: Optional["SeatBasedConfigSchema"] = None
    activity_config: Optional[List["ActivityBasedConfigSchema"]] = None
    outcome_config: Optional[List["OutcomeBasedConfigSchema"]] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class BillingModel(BillingModelInDBBase):
    """Schema for billing model responses"""
    pass


# Specific configuration schemas for different billing types
class SeatBasedConfigSchema(BaseModel):
    """Configuration schema for seat-based billing"""
    price_per_seat: float
    billing_frequency: str = "monthly"  # monthly, quarterly, yearly


class ActivityBasedConfigSchema(BaseModel):
    """Configuration schema for activity-based billing"""
    price_per_action: float
    action_type: str  # api_call, query, completion, etc.


class OutcomeBasedConfigSchema(BaseModel):
    """Configuration schema for outcome-based billing"""
    outcome_type: str  # revenue_uplift, cost_savings, etc.
    percentage: float  # e.g., 5% of revenue uplift


class HybridConfigSchema(BaseModel):
    """Configuration schema for hybrid billing"""
    seat_config: Optional[SeatBasedConfigSchema] = None
    activity_config: Optional[List[ActivityBasedConfigSchema]] = None
    outcome_config: Optional[List[OutcomeBasedConfigSchema]] = None
    base_fee: Optional[float] = None