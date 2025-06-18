from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class BillingModelBase(BaseModel):
    """Base billing model schema"""
    name: str
    description: Optional[str] = None
    model_type: str = Field(..., description="One of: 'agent', 'activity', 'outcome', 'hybrid'")
    is_active: bool = True


class BillingModelCreate(BillingModelBase):
    """Schema for creating billing models"""
    organization_id: int
    
    # Agent-based config fields
    agent_base_agent_fee: Optional[float] = None
    agent_billing_frequency: Optional[str] = "monthly"
    agent_setup_fee: Optional[float] = 0.0
    agent_volume_discount_enabled: Optional[bool] = False
    agent_volume_discount_threshold: Optional[int] = None
    agent_volume_discount_percentage: Optional[float] = None
    agent_tier: Optional[str] = "professional"
    
    # Activity-based config fields
    activity_price_per_action: Optional[float] = None
    activity_action_type: Optional[str] = None
    
    # Outcome-based config fields
    outcome_outcome_type: Optional[str] = None
    outcome_percentage: Optional[float] = None
    
    # Hybrid-specific config
    hybrid_base_fee: Optional[float] = None
    hybrid_agent_config: Optional[AgentBasedConfigSchema] = None
    hybrid_activity_configs: Optional[List[ActivityBasedConfigSchema]] = None
    hybrid_outcome_configs: Optional[List[OutcomeBasedConfigSchema]] = None


class BillingModelUpdate(BaseModel):
    """Schema for updating billing models"""
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = Field(None, description="One of: 'agent', 'activity', 'outcome', 'hybrid'")
    is_active: Optional[bool] = None
    
    # Agent-based config fields
    agent_base_agent_fee: Optional[float] = None
    agent_billing_frequency: Optional[str] = None
    agent_setup_fee: Optional[float] = None
    agent_volume_discount_enabled: Optional[bool] = None
    agent_volume_discount_threshold: Optional[int] = None
    agent_volume_discount_percentage: Optional[float] = None
    agent_tier: Optional[str] = None
    
    # Activity-based config fields
    activity_price_per_action: Optional[float] = None
    activity_action_type: Optional[str] = None
    
    # Outcome-based config fields
    outcome_outcome_type: Optional[str] = None
    outcome_percentage: Optional[float] = None
    
    # Hybrid-specific config
    hybrid_base_fee: Optional[float] = None
    hybrid_agent_config: Optional[AgentBasedConfigSchema] = None
    hybrid_activity_configs: Optional[List[ActivityBasedConfigSchema]] = None
    hybrid_outcome_configs: Optional[List[OutcomeBasedConfigSchema]] = None


class BillingModelInDBBase(BillingModelBase):
    """Base schema for billing models in DB"""
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    # Nested config from dedicated tables
    agent_config: Optional["AgentBasedConfigSchema"] = None
    activity_config: Optional[List["ActivityBasedConfigSchema"]] = None
    outcome_config: Optional[List["OutcomeBasedConfigSchema"]] = None
    hybrid_config: Optional["HybridConfigSchema"] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class BillingModel(BillingModelInDBBase):
    """Schema for billing model responses"""
    pass


# Specific configuration schemas for different billing types
class AgentBasedConfigSchema(BaseModel):
    """Configuration schema for agent-based billing"""
    base_agent_fee: float
    billing_frequency: str = "monthly"  # monthly, yearly
    setup_fee: float = 0.0
    volume_discount_enabled: bool = False
    volume_discount_threshold: Optional[int] = None
    volume_discount_percentage: Optional[float] = None
    agent_tier: str = "professional"  # starter, professional, enterprise


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
    base_fee: float = 0.0


class HybridConfigExtendedSchema(BaseModel):
    """Extended configuration schema for hybrid billing with all components"""
    base_fee: Optional[float] = 0.0
    agent_config: Optional[AgentBasedConfigSchema] = None
    activity_config: Optional[List[ActivityBasedConfigSchema]] = None
    outcome_config: Optional[List[OutcomeBasedConfigSchema]] = None