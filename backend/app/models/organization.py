from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Organization(BaseModel):
    """
    Organization model for grouping users and managing billing settings
    """
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    stripe_customer_id = Column(String, nullable=True, unique=True)
    
    # New fields from revised schema
    external_id = Column(String(255), unique=True, nullable=True)
    status = Column(String(50), nullable=False, default='active')
    billing_email = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    timezone = Column(String(50), nullable=False, default='UTC')
    settings = Column(JSON, nullable=False, default={})
    
    # Relationships
    users = relationship("User", back_populates="organization")
    billing_models = relationship("BillingModel", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")
    api_keys = relationship("ApiKey", back_populates="organization", cascade="all, delete-orphan")
    
    # Integration layer relationships
    integration_connectors = relationship("IntegrationConnector", back_populates="organization")
    integration_webhooks = relationship("IntegrationWebhook", back_populates="organization")
    integration_events = relationship("IntegrationEvent", back_populates="organization")
    integration_streams = relationship("IntegrationStream", back_populates="organization")
    
    def __str__(self) -> str:
        return f"Organization(name={self.name})"