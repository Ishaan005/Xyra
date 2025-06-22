from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class BillingModel(BaseModel):
    """
    BillingModel defines how customers are charged for AI agent usage
    """
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    
    # Billing model type: 'agent', 'activity', 'outcome', 'hybrid', 'workflow'
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
    hybrid_config = relationship(
        "HybridConfig",
        uselist=False,
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
    Configuration for outcome-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    outcome_type = Column(String, nullable=False)  # revenue_uplift, cost_savings, etc.
    percentage = Column(Float, nullable=False)  # e.g., 5% of revenue uplift
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="outcome_config")

class HybridConfig(BaseModel):
    """
    Configuration for hybrid billing - stores base fee and other hybrid-specific settings
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    base_fee = Column(Float, nullable=False, default=0.0)
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="hybrid_config")


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