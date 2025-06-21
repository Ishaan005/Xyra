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
    activity_price_per_unit: Optional[float] = None
    activity_activity_type: Optional[str] = None
    activity_unit_type: Optional[str] = "action"
    activity_base_agent_fee: Optional[float] = 0.0
    activity_volume_pricing_enabled: Optional[bool] = False
    activity_volume_tier_1_threshold: Optional[int] = None
    activity_volume_tier_1_price: Optional[float] = None
    activity_volume_tier_2_threshold: Optional[int] = None
    activity_volume_tier_2_price: Optional[float] = None
    activity_volume_tier_3_threshold: Optional[int] = None
    activity_volume_tier_3_price: Optional[float] = None
    activity_minimum_charge: Optional[float] = 0.0
    activity_billing_frequency: Optional[str] = "monthly"
    activity_is_active: Optional[bool] = True
    
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
    activity_price_per_unit: Optional[float] = None
    activity_activity_type: Optional[str] = None
    activity_unit_type: Optional[str] = None
    activity_base_agent_fee: Optional[float] = None
    activity_volume_pricing_enabled: Optional[bool] = None
    activity_volume_tier_1_threshold: Optional[int] = None
    activity_volume_tier_1_price: Optional[float] = None
    activity_volume_tier_2_threshold: Optional[int] = None
    activity_volume_tier_2_price: Optional[float] = None
    activity_volume_tier_3_threshold: Optional[int] = None
    activity_volume_tier_3_price: Optional[float] = None
    activity_minimum_charge: Optional[float] = None
    activity_billing_frequency: Optional[str] = None
    activity_is_active: Optional[bool] = None
    
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
    """Configuration schema for enhanced activity-based billing"""
    price_per_unit: float
    activity_type: str  # api_call, query, completion, tokens, etc.
    unit_type: str = "action"  # action, token, minute, request, etc.
    base_agent_fee: float = 0.0  # Optional base fee per agent
    volume_pricing_enabled: bool = False
    volume_tier_1_threshold: Optional[int] = None
    volume_tier_1_price: Optional[float] = None
    volume_tier_2_threshold: Optional[int] = None
    volume_tier_2_price: Optional[float] = None
    volume_tier_3_threshold: Optional[int] = None
    volume_tier_3_price: Optional[float] = None
    minimum_charge: float = 0.0
    billing_frequency: str = "monthly"  # monthly, daily, per_use
    is_active: bool = True


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