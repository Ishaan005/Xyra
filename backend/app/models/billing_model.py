from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class BillingModel(BaseModel):
    """
    BillingModel defines how customers are charged for AI agent usage
    """
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    
    # Billing model type: 'agent', 'activity', 'outcome', 'workflow'
    model_type = Column(String, nullable=False)
    
    # Whether this billing model is active
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="billing_models")
    agents = relationship("Agent", back_populates="billing_model")
    # Dedicated config relationships
    agent_config = relationship(
        "AgentBasedConfig",
        uselist=False,
        back_populates="billing_model",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )
    activity_config = relationship(
        "ActivityBasedConfig",
        back_populates="billing_model",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )
    outcome_config = relationship(
        "OutcomeBasedConfig",
        back_populates="billing_model",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )
    workflow_config = relationship(
        "WorkflowBasedConfig",
        uselist=False,
        back_populates="billing_model",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )
    workflow_types = relationship(
        "WorkflowType",
        back_populates="billing_model",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )
    commitment_tiers = relationship(
        "CommitmentTier",
        back_populates="billing_model",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )
    
    def __str__(self) -> str:
        return f"BillingModel(name={self.name}, type={self.model_type})"

class AgentBasedConfig(BaseModel):
    """
    Configuration for agent-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    base_agent_fee = Column(Float, nullable=False)  # Base fee per agent
    billing_frequency = Column(String, nullable=False, default="monthly")  # monthly, yearly
    setup_fee = Column(Float, nullable=True, default=0.0)  # Optional one-time setup fee
    
    # Volume discount configuration
    volume_discount_enabled = Column(Boolean, default=False)
    volume_discount_threshold = Column(Integer, nullable=True)  # Number of agents to qualify for discount
    volume_discount_percentage = Column(Float, nullable=True)  # Discount percentage for volume
    
    # Agent tier configuration (for different agent capabilities)
    agent_tier = Column(String, nullable=False, default="professional")  # starter, professional, enterprise
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="agent_config")

class ActivityBasedConfig(BaseModel):
    """
    Configuration for activity-based billing with enhanced features
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    
    # Basic pricing configuration
    price_per_unit = Column(Float, nullable=False)  # Price per unit of activity
    activity_type = Column(String, nullable=False)  # api_call, query, completion, tokens, etc.
    unit_type = Column(String, nullable=False, default="action")  # action, token, minute, request, etc.
    
    # Optional base agent fee for this activity type
    base_agent_fee = Column(Float, nullable=True, default=0.0)  # Optional base fee per agent
    
    # Volume pricing configuration
    volume_pricing_enabled = Column(Boolean, default=False)
    volume_tier_1_threshold = Column(Integer, nullable=True)  # Units for tier 1 discount
    volume_tier_1_price = Column(Float, nullable=True)  # Price per unit for tier 1
    volume_tier_2_threshold = Column(Integer, nullable=True)  # Units for tier 2 discount
    volume_tier_2_price = Column(Float, nullable=True)  # Price per unit for tier 2
    volume_tier_3_threshold = Column(Integer, nullable=True)  # Units for tier 3 discount
    volume_tier_3_price = Column(Float, nullable=True)  # Price per unit for tier 3
    
    # Minimum billing configuration
    minimum_charge = Column(Float, nullable=True, default=0.0)  # Minimum charge per billing period
    
    # Billing frequency for this activity type
    billing_frequency = Column(String, nullable=False, default="monthly")  # monthly, daily, per_use
    
    # Whether this activity config is active
    is_active = Column(Boolean, default=True)
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="activity_config")

class OutcomeBasedConfig(BaseModel):
    """
    Configuration for sophisticated outcome-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    
    # Outcome identification
    outcome_name = Column(String, nullable=False)  # e.g., "Revenue Uplift", "Cost Savings"
    outcome_type = Column(String, nullable=False)  # revenue_uplift, cost_savings, lead_generation, etc.
    description = Column(String, nullable=True)
    
    # Base platform fee (covers operational costs even if no success)
    base_platform_fee = Column(Float, nullable=False, default=0.0)
    platform_fee_frequency = Column(String, nullable=False, default="monthly")  # monthly, yearly
    
    # Primary outcome pricing
    percentage = Column(Float, nullable=True)  # e.g., 5% of revenue uplift
    fixed_charge_per_outcome = Column(Float, nullable=True) # e.g., $10 per lead
    
    # Success attribution settings
    attribution_window_days = Column(Integer, nullable=False, default=30)  # How long to attribute outcomes
    minimum_attribution_value = Column(Float, nullable=True)  # Minimum value to qualify for billing
    requires_verification = Column(Boolean, default=True)  # Whether outcomes need verification
    
    # Risk adjustment and caps
    success_rate_assumption = Column(Float, nullable=True)  # Expected success rate (e.g., 0.70 = 70%)
    risk_premium_percentage = Column(Float, nullable=False, default=40.0)  # Risk premium (30-50%)
    
    # Performance caps and guarantees
    monthly_cap_amount = Column(Float, nullable=True)  # Maximum billing per month
    success_bonus_threshold = Column(Float, nullable=True)  # Value threshold for bonus
    success_bonus_percentage = Column(Float, nullable=True)  # Additional percentage for exceeding threshold
    
    # Multi-tier outcome pricing
    tier_1_threshold = Column(Float, nullable=True)  # First tier threshold
    tier_1_percentage = Column(Float, nullable=True)  # Percentage for tier 1
    tier_2_threshold = Column(Float, nullable=True)  # Second tier threshold
    tier_2_percentage = Column(Float, nullable=True)  # Percentage for tier 2
    tier_3_threshold = Column(Float, nullable=True)  # Third tier threshold
    tier_3_percentage = Column(Float, nullable=True)  # Percentage for tier 3
    
    # Billing configuration
    billing_frequency = Column(String, nullable=False, default="monthly")  # monthly, quarterly
    currency = Column(String, nullable=False, default="USD")
    
    # Status and settings
    is_active = Column(Boolean, default=True)
    auto_bill_verified_outcomes = Column(Boolean, default=False)  # Auto-bill verified outcomes
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="outcome_config")

class WorkflowBasedConfig(BaseModel):
    """
    Configuration for workflow-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    
    # Base platform fee (monthly/yearly subscription component)
    base_platform_fee = Column(Float, nullable=False, default=0.0)
    platform_fee_frequency = Column(String, nullable=False, default="monthly")  # monthly, yearly
    
    # Default billing frequency for workflows (can be overridden per workflow type)
    default_billing_frequency = Column(String, nullable=False, default="monthly")
    
    # Volume discount configuration
    volume_discount_enabled = Column(Boolean, default=False)
    volume_discount_threshold = Column(Integer, nullable=True)  # Number of workflows to qualify
    volume_discount_percentage = Column(Float, nullable=True)  # Discount percentage
    
    # Overage pricing for workflows beyond commitment
    overage_multiplier = Column(Float, nullable=False, default=1.0)  # 1.0 = normal price, 1.5 = 150% of normal
    
    # Currency for all pricing
    currency = Column(String, nullable=False, default="USD")
    
    # Whether this workflow config is active
    is_active = Column(Boolean, default=True)
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="workflow_config")


class WorkflowType(BaseModel):
    """
    Individual workflow types with their pricing and configuration
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    
    # Workflow identification
    workflow_name = Column(String, nullable=False)  # e.g., "Lead Research", "Cash Flow Forecast"
    workflow_type = Column(String, nullable=False)  # e.g., "lead_research", "financial_forecast"
    description = Column(String, nullable=True)
    
    # Pricing configuration
    price_per_workflow = Column(Float, nullable=False)  # Price per complete workflow execution
    
    # Resource estimation (for cost monitoring)
    estimated_compute_cost = Column(Float, nullable=True, default=0.0)  # Internal cost tracking
    estimated_duration_minutes = Column(Integer, nullable=True)  # Expected duration
    complexity_level = Column(String, nullable=False, default="medium")  # simple, medium, complex
    
    # Business value metrics
    expected_roi_multiplier = Column(Float, nullable=True)  # Expected ROI multiple for customers
    business_value_category = Column(String, nullable=True)  # lead_generation, cost_savings, revenue_growth
    
    # Volume pricing tiers (optional per workflow type)
    volume_tier_1_threshold = Column(Integer, nullable=True)
    volume_tier_1_price = Column(Float, nullable=True)
    volume_tier_2_threshold = Column(Integer, nullable=True)
    volume_tier_2_price = Column(Float, nullable=True)
    volume_tier_3_threshold = Column(Integer, nullable=True)
    volume_tier_3_price = Column(Float, nullable=True)
    
    # Billing configuration
    billing_frequency = Column(String, nullable=True)  # If null, uses default from WorkflowBasedConfig
    minimum_charge = Column(Float, nullable=True, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="workflow_types")


class CommitmentTier(BaseModel):
    """
    Commitment tiers for workflow-based billing (e.g., minimum monthly workflows)
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    
    # Tier identification
    tier_name = Column(String, nullable=False)  # e.g., "Starter", "Growth", "Scale"
    tier_level = Column(Integer, nullable=False)  # 1, 2, 3... for ordering
    description = Column(String, nullable=True)
    
    # Commitment requirements
    minimum_workflows_per_month = Column(Integer, nullable=False)  # Total workflows across all types
    minimum_monthly_revenue = Column(Float, nullable=False)  # Guaranteed minimum revenue
    
    # Included quantities (workflows included in base fee)
    included_workflows = Column(Integer, nullable=False, default=0)
    included_workflow_types = Column(String, nullable=True)  # JSON string of workflow types included
    
    # Pricing benefits
    discount_percentage = Column(Float, nullable=True, default=0.0)  # Discount on per-workflow pricing
    platform_fee_discount = Column(Float, nullable=True, default=0.0)  # Discount on platform fee
    
    # Contract terms
    commitment_period_months = Column(Integer, nullable=False, default=12)  # Contract length
    overage_rate_multiplier = Column(Float, nullable=False, default=1.0)  # Pricing for workflows beyond commitment
    
    # Status
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)  # For UI highlighting
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="commitment_tiers")


class OutcomeMetric(BaseModel):
    """
    Individual outcome metrics for tracking and verification
    """
    outcome_config_id = Column(Integer, ForeignKey("outcomebasedconfig.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agent.id", ondelete="CASCADE"), nullable=False)
    
    # Outcome details
    outcome_value = Column(Float, nullable=False)  # The measured outcome value
    outcome_currency = Column(String, nullable=False, default="USD")
    
    # Attribution and verification
    attribution_start_date = Column(DateTime, nullable=False)
    attribution_end_date = Column(DateTime, nullable=False)
    verification_status = Column(String, nullable=False, default="pending")  # pending, verified, rejected
    verification_notes = Column(String, nullable=True)
    verified_by = Column(String, nullable=True)  # User ID or system that verified
    verified_at = Column(DateTime, nullable=True)
    
    # Calculation details
    calculated_fee = Column(Float, nullable=False)  # Fee calculated for this outcome
    tier_applied = Column(String, nullable=True)  # Which tier was applied
    bonus_applied = Column(Float, nullable=True, default=0.0)  # Any bonus applied
    
    # Billing status
    billing_status = Column(String, nullable=False, default="pending")  # pending, billed, disputed
    billed_at = Column(DateTime, nullable=True)
    billing_period = Column(String, nullable=True)  # e.g., "2025-01"
    
    # Metadata
    outcome_data = Column(String, nullable=True)  # JSON metadata about the outcome
    
    # Relationships
    outcome_config = relationship("OutcomeBasedConfig", backref="outcome_metrics")
    agent = relationship("Agent", backref="outcome_metrics")


class OutcomeVerificationRule(BaseModel):
    """
    Rules for automatic outcome verification
    """
    outcome_config_id = Column(Integer, ForeignKey("outcomebasedconfig.id", ondelete="CASCADE"), nullable=False)
    
    # Rule identification
    rule_name = Column(String, nullable=False)
    rule_type = Column(String, nullable=False)  # api_integration, manual_review, threshold_based
    
    # Verification criteria
    verification_method = Column(String, nullable=False)  # webhook, api_pull, manual, analytics_integration
    api_endpoint = Column(String, nullable=True)  # For API-based verification
    verification_threshold = Column(Float, nullable=True)  # Minimum value for auto-verification
    
    # Rule configuration
    rule_config = Column(String, nullable=True)  # JSON configuration for the rule
    is_active = Column(Boolean, default=True)
    
    # Relationship
    outcome_config = relationship("OutcomeBasedConfig", backref="verification_rules")