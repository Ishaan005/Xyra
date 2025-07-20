from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class BillingModelBase(BaseModel):
    """Base billing model schema"""
    name: str
    description: Optional[str] = None
    model_type: str = Field(..., description="One of: 'agent', 'activity', 'outcome', 'workflow'")
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
    outcome_outcome_name: Optional[str] = None
    outcome_outcome_type: Optional[str] = None
    outcome_description: Optional[str] = None
    outcome_base_platform_fee: Optional[float] = None
    outcome_platform_fee_frequency: Optional[str] = None
    outcome_percentage: Optional[float] = None
    outcome_fixed_charge_per_outcome: Optional[float] = None
    outcome_attribution_window_days: Optional[int] = None
    outcome_minimum_attribution_value: Optional[float] = None
    outcome_requires_verification: Optional[bool] = None
    outcome_success_rate_assumption: Optional[float] = None
    outcome_risk_premium_percentage: Optional[float] = None
    outcome_monthly_cap_amount: Optional[float] = None
    outcome_success_bonus_threshold: Optional[float] = None
    outcome_success_bonus_percentage: Optional[float] = None
    outcome_tier_1_threshold: Optional[float] = None
    outcome_tier_1_percentage: Optional[float] = None
    outcome_tier_2_threshold: Optional[float] = None
    outcome_tier_2_percentage: Optional[float] = None
    outcome_tier_3_threshold: Optional[float] = None
    outcome_tier_3_percentage: Optional[float] = None
    outcome_billing_frequency: Optional[str] = None
    outcome_currency: Optional[str] = None
    outcome_is_active: Optional[bool] = None
    outcome_auto_bill_verified_outcomes: Optional[bool] = None
    
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
    model_type: Optional[str] = Field(None, description="One of: 'agent', 'activity', 'outcome', 'workflow'")
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
    outcome_outcome_name: Optional[str] = None
    outcome_outcome_type: Optional[str] = None
    outcome_description: Optional[str] = None
    outcome_base_platform_fee: Optional[float] = None
    outcome_platform_fee_frequency: Optional[str] = None
    outcome_percentage: Optional[float] = None
    outcome_fixed_charge_per_outcome: Optional[float] = None
    outcome_attribution_window_days: Optional[int] = None
    outcome_minimum_attribution_value: Optional[float] = None
    outcome_requires_verification: Optional[bool] = None
    outcome_success_rate_assumption: Optional[float] = None
    outcome_risk_premium_percentage: Optional[float] = None
    outcome_monthly_cap_amount: Optional[float] = None
    outcome_success_bonus_threshold: Optional[float] = None
    outcome_success_bonus_percentage: Optional[float] = None
    outcome_tier_1_threshold: Optional[float] = None
    outcome_tier_1_percentage: Optional[float] = None
    outcome_tier_2_threshold: Optional[float] = None
    outcome_tier_2_percentage: Optional[float] = None
    outcome_tier_3_threshold: Optional[float] = None
    outcome_tier_3_percentage: Optional[float] = None
    outcome_billing_frequency: Optional[str] = None
    outcome_currency: Optional[str] = None
    outcome_is_active: Optional[bool] = None
    outcome_auto_bill_verified_outcomes: Optional[bool] = None
    
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
    # Nested config from dedicated tables - using the actual SQLAlchemy model names
    agent_config: Optional["AgentBasedConfigSchema"] = None
    activity_config: Optional[List["ActivityBasedConfigSchema"]] = None
    outcome_config: Optional[List["OutcomeBasedConfigSchema"]] = None
    workflow_config: Optional["WorkflowBasedConfigSchema"] = None
    workflow_types: Optional[List["WorkflowTypeSchema"]] = None
    commitment_tiers: Optional[List["CommitmentTierSchema"]] = None
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class BillingModel(BillingModelInDBBase):
    """Schema for billing model responses with flattened convenience fields"""
    
    # Flattened convenience fields for frontend compatibility
    # Agent config flattened fields
    agent_base_agent_fee: Optional[float] = Field(None, description="Computed from agent_config")
    agent_billing_frequency: Optional[str] = Field(None, description="Computed from agent_config")
    agent_setup_fee: Optional[float] = Field(None, description="Computed from agent_config")
    agent_volume_discount_enabled: Optional[bool] = Field(None, description="Computed from agent_config")
    agent_volume_discount_threshold: Optional[int] = Field(None, description="Computed from agent_config")
    agent_volume_discount_percentage: Optional[float] = Field(None, description="Computed from agent_config")
    agent_tier: Optional[str] = Field(None, description="Computed from agent_config")
    
    # Activity config flattened fields (first active config)
    activity_price_per_unit: Optional[float] = Field(None, description="Computed from activity_config[0]")
    activity_activity_type: Optional[str] = Field(None, description="Computed from activity_config[0]")
    activity_unit_type: Optional[str] = Field(None, description="Computed from activity_config[0]")
    activity_base_agent_fee: Optional[float] = Field(None, description="Computed from activity_config[0]")
    activity_volume_pricing_enabled: Optional[bool] = Field(None, description="Computed from activity_config[0]")
    activity_volume_tier_1_threshold: Optional[int] = Field(None, description="Computed from activity_config[0]")
    activity_volume_tier_1_price: Optional[float] = Field(None, description="Computed from activity_config[0]")
    activity_volume_tier_2_threshold: Optional[int] = Field(None, description="Computed from activity_config[0]")
    activity_volume_tier_2_price: Optional[float] = Field(None, description="Computed from activity_config[0]")
    activity_volume_tier_3_threshold: Optional[int] = Field(None, description="Computed from activity_config[0]")
    activity_volume_tier_3_price: Optional[float] = Field(None, description="Computed from activity_config[0]")
    activity_minimum_charge: Optional[float] = Field(None, description="Computed from activity_config[0]")
    activity_billing_frequency: Optional[str] = Field(None, description="Computed from activity_config[0]")
    activity_is_active: Optional[bool] = Field(None, description="Computed from activity_config[0]")
    
    # Outcome config flattened fields (first active config)
    outcome_outcome_name: Optional[str] = Field(None, description="Computed from outcome_config[0]")
    outcome_outcome_type: Optional[str] = Field(None, description="Computed from outcome_config[0]")
    outcome_description: Optional[str] = Field(None, description="Computed from outcome_config[0]")
    outcome_base_platform_fee: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_platform_fee_frequency: Optional[str] = Field(None, description="Computed from outcome_config[0]")
    outcome_percentage: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_fixed_charge_per_outcome: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_attribution_window_days: Optional[int] = Field(None, description="Computed from outcome_config[0]")
    outcome_minimum_attribution_value: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_requires_verification: Optional[bool] = Field(None, description="Computed from outcome_config[0]")
    outcome_success_rate_assumption: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_risk_premium_percentage: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_monthly_cap_amount: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_success_bonus_threshold: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_success_bonus_percentage: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_tier_1_threshold: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_tier_1_percentage: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_tier_2_threshold: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_tier_2_percentage: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_tier_3_threshold: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_tier_3_percentage: Optional[float] = Field(None, description="Computed from outcome_config[0]")
    outcome_billing_frequency: Optional[str] = Field(None, description="Computed from outcome_config[0]")
    outcome_currency: Optional[str] = Field(None, description="Computed from outcome_config[0]")
    outcome_is_active: Optional[bool] = Field(None, description="Computed from outcome_config[0]")
    outcome_auto_bill_verified_outcomes: Optional[bool] = Field(None, description="Computed from outcome_config[0]")
    
    # Workflow config flattened fields
    workflow_base_platform_fee: Optional[float] = Field(None, description="Computed from workflow_config")
    workflow_platform_fee_frequency: Optional[str] = Field(None, description="Computed from workflow_config")
    workflow_default_billing_frequency: Optional[str] = Field(None, description="Computed from workflow_config")
    workflow_volume_discount_enabled: Optional[bool] = Field(None, description="Computed from workflow_config")
    workflow_volume_discount_threshold: Optional[int] = Field(None, description="Computed from workflow_config")
    workflow_volume_discount_percentage: Optional[float] = Field(None, description="Computed from workflow_config")
    workflow_overage_multiplier: Optional[float] = Field(None, description="Computed from workflow_config")
    workflow_currency: Optional[str] = Field(None, description="Computed from workflow_config")
    workflow_is_active: Optional[bool] = Field(None, description="Computed from workflow_config")
    
    def model_post_init(self, __context) -> None:
        """Post-initialization hook to populate flattened fields from nested config"""
        # Flatten agent config
        if self.agent_config:
            cfg = self.agent_config
            self.agent_base_agent_fee = cfg.base_agent_fee
            self.agent_billing_frequency = cfg.billing_frequency
            self.agent_setup_fee = cfg.setup_fee
            self.agent_volume_discount_enabled = cfg.volume_discount_enabled
            self.agent_volume_discount_threshold = cfg.volume_discount_threshold
            self.agent_volume_discount_percentage = cfg.volume_discount_percentage
            self.agent_tier = cfg.agent_tier
        
        # Flatten activity config (use first active config)
        if self.activity_config:
            for cfg in self.activity_config:
                if cfg.is_active:
                    self.activity_price_per_unit = cfg.price_per_unit
                    self.activity_activity_type = cfg.activity_type
                    self.activity_unit_type = cfg.unit_type
                    self.activity_base_agent_fee = cfg.base_agent_fee
                    self.activity_volume_pricing_enabled = cfg.volume_pricing_enabled
                    self.activity_volume_tier_1_threshold = cfg.volume_tier_1_threshold
                    self.activity_volume_tier_1_price = cfg.volume_tier_1_price
                    self.activity_volume_tier_2_threshold = cfg.volume_tier_2_threshold
                    self.activity_volume_tier_2_price = cfg.volume_tier_2_price
                    self.activity_volume_tier_3_threshold = cfg.volume_tier_3_threshold
                    self.activity_volume_tier_3_price = cfg.volume_tier_3_price
                    self.activity_minimum_charge = cfg.minimum_charge
                    self.activity_billing_frequency = cfg.billing_frequency
                    self.activity_is_active = cfg.is_active
                    break
        
        # Flatten outcome config (use first active config)
        if self.outcome_config:
            for cfg in self.outcome_config:
                if cfg.is_active:
                    self.outcome_outcome_name = cfg.outcome_name
                    self.outcome_outcome_type = cfg.outcome_type
                    self.outcome_description = cfg.description
                    self.outcome_base_platform_fee = cfg.base_platform_fee
                    self.outcome_platform_fee_frequency = cfg.platform_fee_frequency
                    self.outcome_percentage = cfg.percentage
                    self.outcome_fixed_charge_per_outcome = cfg.fixed_charge_per_outcome
                    self.outcome_attribution_window_days = cfg.attribution_window_days
                    self.outcome_minimum_attribution_value = cfg.minimum_attribution_value
                    self.outcome_requires_verification = cfg.requires_verification
                    self.outcome_success_rate_assumption = cfg.success_rate_assumption
                    self.outcome_risk_premium_percentage = cfg.risk_premium_percentage
                    self.outcome_monthly_cap_amount = cfg.monthly_cap_amount
                    self.outcome_success_bonus_threshold = cfg.success_bonus_threshold
                    self.outcome_success_bonus_percentage = cfg.success_bonus_percentage
                    self.outcome_tier_1_threshold = cfg.tier_1_threshold
                    self.outcome_tier_1_percentage = cfg.tier_1_percentage
                    self.outcome_tier_2_threshold = cfg.tier_2_threshold
                    self.outcome_tier_2_percentage = cfg.tier_2_percentage
                    self.outcome_tier_3_threshold = cfg.tier_3_threshold
                    self.outcome_tier_3_percentage = cfg.tier_3_percentage
                    self.outcome_billing_frequency = cfg.billing_frequency
                    self.outcome_currency = cfg.currency
                    self.outcome_is_active = cfg.is_active
                    self.outcome_auto_bill_verified_outcomes = cfg.auto_bill_verified_outcomes
                    break
        
        # Flatten workflow config
        if self.workflow_config:
            cfg = self.workflow_config
            self.workflow_base_platform_fee = cfg.base_platform_fee
            self.workflow_platform_fee_frequency = cfg.platform_fee_frequency
            self.workflow_default_billing_frequency = cfg.default_billing_frequency
            self.workflow_volume_discount_enabled = cfg.volume_discount_enabled
            self.workflow_volume_discount_threshold = cfg.volume_discount_threshold
            self.workflow_volume_discount_percentage = cfg.volume_discount_percentage
            self.workflow_overage_multiplier = cfg.overage_multiplier
            self.workflow_currency = cfg.currency
            self.workflow_is_active = cfg.is_active


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
    
    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True


class OutcomeBasedConfigSchema(BaseModel):
    """Configuration schema for sophisticated outcome-based billing"""
    # Outcome identification
    outcome_name: str  # e.g., "Revenue Uplift", "Cost Savings"
    outcome_type: str  # revenue_uplift, cost_savings, lead_generation, etc.
    description: Optional[str] = None
    
    # Base platform fee (covers operational costs even if no success)
    base_platform_fee: float = 0.0
    platform_fee_frequency: str = "monthly"  # monthly, yearly
    
    # Primary outcome pricing
    percentage: Optional[float] = None  # e.g., 5% of revenue uplift
    fixed_charge_per_outcome: Optional[float] = None  # e.g., $10 per lead
    
    # Success attribution settings
    attribution_window_days: int = 30  # How long to attribute outcomes
    minimum_attribution_value: Optional[float] = None  # Minimum value to qualify for billing
    requires_verification: bool = True  # Whether outcomes need verification
    
    # Risk adjustment and caps
    success_rate_assumption: Optional[float] = None  # Expected success rate (e.g., 0.70 = 70%)
    risk_premium_percentage: float = 40.0  # Risk premium (30-50%)
    
    # Performance caps and guarantees
    monthly_cap_amount: Optional[float] = None  # Maximum billing per month
    success_bonus_threshold: Optional[float] = None  # Value threshold for bonus
    success_bonus_percentage: Optional[float] = None  # Additional percentage for exceeding threshold
    
    # Multi-tier outcome pricing
    tier_1_threshold: Optional[float] = None  # First tier threshold
    tier_1_percentage: Optional[float] = None  # Percentage for tier 1
    tier_2_threshold: Optional[float] = None  # Second tier threshold
    tier_2_percentage: Optional[float] = None  # Percentage for tier 2
    tier_3_threshold: Optional[float] = None  # Third tier threshold
    tier_3_percentage: Optional[float] = None  # Percentage for tier 3
    
    # Billing configuration
    billing_frequency: str = "monthly"  # monthly, quarterly
    currency: str = "USD"
    
    # Status and settings
    is_active: bool = True
    auto_bill_verified_outcomes: bool = False  # Auto-bill verified outcomes
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True


class OutcomeMetricSchema(BaseModel):
    """Schema for outcome metrics tracking"""
    id: Optional[int] = None
    outcome_config_id: int
    agent_id: int
    
    # Outcome details
    outcome_value: float
    outcome_currency: str = "USD"
    
    # Attribution and verification
    attribution_start_date: datetime
    attribution_end_date: datetime
    verification_status: str = "pending"  # pending, verified, rejected
    verification_notes: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    
    # Calculation details
    calculated_fee: float
    tier_applied: Optional[str] = None
    bonus_applied: float = 0.0
    
    # Billing status
    billing_status: str = "pending"  # pending, billed, disputed
    billed_at: Optional[datetime] = None
    billing_period: Optional[str] = None
    
    # Metadata
    outcome_data: Optional[str] = None  # JSON metadata
    
    class Config:
        from_attributes = True


class OutcomeVerificationRuleSchema(BaseModel):
    """Schema for outcome verification rules"""
    id: Optional[int] = None
    outcome_config_id: int
    
    # Rule identification
    rule_name: str
    rule_type: str  # api_integration, manual_review, threshold_based
    
    # Verification criteria
    verification_method: str  # webhook, api_pull, manual, analytics_integration
    api_endpoint: Optional[str] = None
    verification_threshold: Optional[float] = None
    
    # Rule configuration
    rule_config: Optional[str] = None  # JSON configuration
    is_active: bool = True
    
    class Config:
        from_attributes = True


class OutcomeMetricCreate(BaseModel):
    """Schema for creating outcome metrics"""
    agent_id: int
    outcome_value: float
    outcome_currency: str = "USD"
    attribution_start_date: datetime
    attribution_end_date: datetime
    outcome_data: Optional[Dict[str, Any]] = None


class OutcomeMetricUpdate(BaseModel):
    """Schema for updating outcome metrics"""
    outcome_value: Optional[float] = None
    verification_status: Optional[str] = None
    verification_notes: Optional[str] = None
    verified_by: Optional[str] = None
    billing_status: Optional[str] = None
    outcome_data: Optional[Dict[str, Any]] = None