"""
Agent service module - modularized for better organization and maintainability.
"""

from .core import (
    get_agent,
    get_agent_by_external_id,
    get_agents_by_organization,
    create_agent,
    update_agent,
    delete_agent
)

from .activity import (
    record_agent_activity
)

from .cost import (
    record_agent_cost
)

from .outcome import (
    record_agent_outcome
)

from .workflow import (
    record_agent_workflow,
    record_bulk_workflows
)

from .billing import (
    get_agent_billing_config,
    validate_agent_billing_data,
    validate_workflow_billing_data
)

from .statistics import (
    get_agent_stats,
    get_agent_billing_summary
)

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
