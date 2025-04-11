from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Organization(BaseModel):
    """
    Organization model for grouping users and managing billing settings
    """
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    stripe_customer_id = Column(String, nullable=True, unique=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    billing_models = relationship("BillingModel", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")
    
    def __str__(self) -> str:
        return f"Organization(name={self.name})"