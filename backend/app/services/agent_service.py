"""
Agent service module - now modularized for better organization and maintainability.

This module provides a backward-compatible interface by importing all functions
from the modularized sub-modules. All existing imports will continue to work.
"""

# Import all functions from the modularized sub-modules
from app.services.agent import (
    # Core operations
    get_agent,
    get_agent_by_external_id,
    get_agents_by_organization,
    create_agent,
    update_agent,
    delete_agent,
    
    # Activity operations
    record_agent_activity,
    
    # Cost operations
    record_agent_cost,
    
    # Outcome operations
    record_agent_outcome,
    
    # Workflow operations
    record_agent_workflow,
    record_bulk_workflows,
    
    # Billing operations
    get_agent_billing_config,
    validate_agent_billing_data,
    validate_workflow_billing_data,
    
    # Statistics operations
    get_agent_stats,
    get_agent_billing_summary
)

# Export all functions for backward compatibility
__all__ = [
    # Core operations
    "get_agent",
    "get_agent_by_external_id",
    "get_agents_by_organization",
    "create_agent",
    "update_agent",
    "delete_agent",
    
    # Activity operations
    "record_agent_activity",
    
    # Cost operations
    "record_agent_cost",
    
    # Outcome operations
    "record_agent_outcome",
    
    # Workflow operations
    "record_agent_workflow",
    "record_bulk_workflows",
    
    # Billing operations
    "get_agent_billing_config",
    "validate_agent_billing_data",
    "validate_workflow_billing_data",
    
    # Statistics operations
    "get_agent_stats",
    "get_agent_billing_summary"
]