from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class BillingModelBase(BaseModel):
    """Base billing model schema"""
    name: str
    description: Optional[str] = None
    model_type: str = Field(..., description="One of: 'agent', 'activity', 'outcome', 'hybrid', 'workflow'")
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
    
    # Workflow-based config fields
    workflow_base_platform_fee: Optional[float] = None
    workflow_platform_fee_frequency: Optional[str] = "monthly"
    workflow_default_billing_frequency: Optional[str] = "monthly"
    workflow_volume_discount_enabled: Optional[bool] = False
    workflow_volume_discount_threshold: Optional[int] = None
    workflow_volume_discount_percentage: Optional[float] = None
    workflow_overage_multiplier: Optional[float] = 1.0
    workflow_currency: Optional[str] = "USD"
    workflow_is_active: Optional[bool] = True
    workflow_types: Optional[List[WorkflowTypeSchema]] = None
    commitment_tiers: Optional[List[CommitmentTierSchema]] = None


class BillingModelUpdate(BaseModel):
    """Schema for updating billing models"""
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = Field(None, description="One of: 'agent', 'activity', 'outcome', 'hybrid', 'workflow'")
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
    
    # Workflow-based config fields
    workflow_base_platform_fee: Optional[float] = None
    workflow_platform_fee_frequency: Optional[str] = None
    workflow_default_billing_frequency: Optional[str] = None
    workflow_volume_discount_enabled: Optional[bool] = None
    workflow_volume_discount_threshold: Optional[int] = None
    workflow_volume_discount_percentage: Optional[float] = None
    workflow_overage_multiplier: Optional[float] = None
    workflow_currency: Optional[str] = None
    workflow_is_active: Optional[bool] = None
    workflow_types: Optional[List[WorkflowTypeSchema]] = None
    commitment_tiers: Optional[List[CommitmentTierSchema]] = None


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
    workflow_config: Optional["WorkflowBasedConfigSchema"] = None
    workflow_types: Optional[List["WorkflowTypeSchema"]] = None
    commitment_tiers: Optional[List["CommitmentTierSchema"]] = None
    
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


class WorkflowBasedConfigSchema(BaseModel):
    """Configuration schema for workflow-based billing"""
    base_platform_fee: float = 0.0
    platform_fee_frequency: str = "monthly"  # monthly, yearly
    default_billing_frequency: str = "monthly"
    volume_discount_enabled: bool = False
    volume_discount_threshold: Optional[int] = None
    volume_discount_percentage: Optional[float] = None
    overage_multiplier: float = 1.0
    currency: str = "USD"
    is_active: bool = True


class WorkflowTypeSchema(BaseModel):
    """Schema for individual workflow types within workflow-based billing"""
    workflow_name: str  # e.g., "Lead Research", "Cash Flow Forecast"
    workflow_type: str  # e.g., "lead_research", "financial_forecast"
    description: Optional[str] = None
    price_per_workflow: float
    
    # Resource estimation
    estimated_compute_cost: Optional[float] = 0.0
    estimated_duration_minutes: Optional[int] = None
    complexity_level: str = "medium"  # simple, medium, complex
    
    # Business value metrics
    expected_roi_multiplier: Optional[float] = None
    business_value_category: Optional[str] = None  # lead_generation, cost_savings, revenue_growth
    
    # Volume pricing tiers
    volume_tier_1_threshold: Optional[int] = None
    volume_tier_1_price: Optional[float] = None
    volume_tier_2_threshold: Optional[int] = None
    volume_tier_2_price: Optional[float] = None
    volume_tier_3_threshold: Optional[int] = None
    volume_tier_3_price: Optional[float] = None
    
    # Billing configuration
    billing_frequency: Optional[str] = None  # If null, uses default from WorkflowBasedConfig
    minimum_charge: Optional[float] = 0.0
    is_active: bool = True


class CommitmentTierSchema(BaseModel):
    """Schema for commitment tiers in workflow-based billing"""
    tier_name: str  # e.g., "Starter", "Growth", "Scale"
    tier_level: int  # 1, 2, 3... for ordering
    description: Optional[str] = None
    
    # Commitment requirements
    minimum_workflows_per_month: int
    minimum_monthly_revenue: float
    
    # Included quantities
    included_workflows: int = 0
    included_workflow_types: Optional[str] = None  # JSON string of workflow types
    
    # Pricing benefits
    discount_percentage: Optional[float] = 0.0
    platform_fee_discount: Optional[float] = 0.0
    
    # Contract terms
    commitment_period_months: int = 12
    overage_rate_multiplier: float = 1.0
    
    # Status
    is_active: bool = True
    is_popular: bool = False