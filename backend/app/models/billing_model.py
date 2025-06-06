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
    
    # Billing model type: 'seat', 'activity', 'outcome', 'hybrid'
    model_type = Column(String, nullable=False)
    
    # Whether this billing model is active
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="billing_models")
    agents = relationship("Agent", back_populates="billing_model")
    # Dedicated config relationships
    seat_config = relationship(
        "SeatBasedConfig",
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
    
    def __str__(self) -> str:
        return f"BillingModel(name={self.name}, type={self.model_type})"

class SeatBasedConfig(BaseModel):
    """
    Configuration for seat-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    price_per_seat = Column(Float, nullable=False)
    billing_frequency = Column(String, nullable=False, default="monthly")  # monthly, quarterly, yearly
    
    # Relationship
    billing_model = relationship("BillingModel", back_populates="seat_config")

class ActivityBasedConfig(BaseModel):
    """
    Configuration for activity-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id", ondelete="CASCADE"), nullable=False)
    price_per_action = Column(Float, nullable=False)
    action_type = Column(String, nullable=False)  # api_call, query, task, etc.
    
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