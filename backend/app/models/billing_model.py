from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean, JSON
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
    
    # Configuration stored as JSON
    config = Column(JSON, nullable=False, default={})
    
    # Whether this billing model is active
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="billing_models")
    agents = relationship("Agent", back_populates="billing_model")
    
    def __str__(self) -> str:
        return f"BillingModel(name={self.name}, type={self.model_type})"

class SeatBasedConfig(BaseModel):
    """
    Configuration for seat-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id"), nullable=False)
    price_per_seat = Column(Float, nullable=False)
    billing_frequency = Column(String, nullable=False, default="monthly")  # monthly, quarterly, yearly
    
    # Relationship
    billing_model = relationship("BillingModel", backref="seat_config")

class ActivityBasedConfig(BaseModel):
    """
    Configuration for activity-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id"), nullable=False)
    price_per_action = Column(Float, nullable=False)
    action_type = Column(String, nullable=False)  # api_call, query, task, etc.
    
    # Relationship
    billing_model = relationship("BillingModel", backref="activity_config")

class OutcomeBasedConfig(BaseModel):
    """
    Configuration for outcome-based billing
    """
    billing_model_id = Column(Integer, ForeignKey("billingmodel.id"), nullable=False)
    outcome_type = Column(String, nullable=False)  # revenue_uplift, cost_savings, etc.
    percentage = Column(Float, nullable=False)  # e.g., 5% of revenue uplift
    
    # Relationship
    billing_model = relationship("BillingModel", backref="outcome_config")