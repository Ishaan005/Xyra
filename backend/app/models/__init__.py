"""
Models package for the Xyra backend application.
"""

# Import all models to ensure they are registered with SQLAlchemy
from .base import BaseModel
from .user import User
from .organization import Organization
from .billing_model import (
    BillingModel, AgentBasedConfig, ActivityBasedConfig, OutcomeBasedConfig,
    HybridConfig, WorkflowBasedConfig, WorkflowType, CommitmentTier,
    OutcomeMetric, OutcomeVerificationRule
)
from .agent import Agent, AgentActivity, AgentCost, AgentOutcome
from .invoice import Invoice, InvoiceLineItem
from .integration import IntegrationConnector, IntegrationWebhook, IntegrationEvent, IntegrationStream

# Export all models
__all__ = [
    "BaseModel",
    "User",
    "Organization", 
    "BillingModel",
    "AgentBasedConfig",
    "ActivityBasedConfig", 
    "OutcomeBasedConfig",
    "HybridConfig",
    "WorkflowBasedConfig",
    "WorkflowType",
    "CommitmentTier",
    "OutcomeMetric",
    "OutcomeVerificationRule",
    "Agent",
    "AgentActivity",
    "AgentCost",
    "AgentOutcome",
    "Invoice",
    "InvoiceLineItem",
    "IntegrationConnector",
    "IntegrationWebhook", 
    "IntegrationEvent",
    "IntegrationStream"
]
