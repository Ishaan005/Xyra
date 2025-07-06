"""
Xyra Client SDK Examples

This file contains comprehensive examples showing how to use the Xyra Client SDK
for different billing models and use cases.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any
from xyra_client import XyraClient


# Example 1: Basic Client Setup
def example_basic_setup():
    """Basic client setup with environment variables."""
    client = XyraClient(
        base_url=os.getenv("XYRA_BASE_URL", "http://localhost:8000"),
        agent_id=int(os.getenv("XYRA_AGENT_ID", "1")),
        token=os.getenv("XYRA_TOKEN", "your-token-here")
    )
    return client


# Example 2: Agent-Based Billing Model
async def example_agent_based_billing():
    """Example for agent-based billing model."""
    client = example_basic_setup()
    
    print("=== Agent-Based Billing Example ===")
    
    # Check agent health and billing configuration
    health = await client.health_check()
    print(f"Agent health: {health['status']}")
    
    # Get billing model info
    billing_info = await client.get_billing_model_info()
    print(f"Billing model: {billing_info['model_type']}")
    
    # Smart track for agent usage
    result = await client.smart_track(metadata={"session_id": "session_123"})
    print(f"Recorded agent usage: {result}")
    
    # Get billing summary
    summary = await client.get_billing_summary()
    print(f"Billing summary: {summary}")


# Example 3: Activity-Based Billing Model
async def example_activity_based_billing():
    """Example for activity-based billing model."""
    client = example_basic_setup()
    
    print("=== Activity-Based Billing Example ===")
    
    # Get supported activities
    activities = await client.get_supported_activities()
    print(f"Supported activities: {activities}")
    
    # Record specific activity
    if activities:
        result = await client.record_activity(
            activity_type=activities[0],
            metadata={"batch_id": "batch_456", "records_processed": 1000}
        )
        print(f"Activity recorded: {result}")
    
    # Auto-record all configured activities
    auto_result = await client.record_activities_auto(
        metadata={"session_id": "session_789"}
    )
    print(f"Auto-recorded activities: {auto_result}")
    
    # Use smart tracking for activity-based model
    smart_result = await client.smart_track(
        activity_units=5,
        metadata={"operation": "data_processing"}
    )
    print(f"Smart tracked activities: {smart_result}")


# Example 4: Outcome-Based Billing Model
async def example_outcome_based_billing():
    """Example for outcome-based billing model."""
    client = example_basic_setup()
    
    print("=== Outcome-Based Billing Example ===")
    
    # Get supported outcomes
    outcomes = await client.get_supported_outcomes()
    print(f"Supported outcomes: {outcomes}")
    
    # Record specific outcome
    if outcomes:
        result = await client.record_outcome(
            outcome_type=outcomes[0],
            value=500.0,
            currency="USD",
            details={"deal_id": "D123", "customer": "Acme Corp"},
            verified=True
        )
        print(f"Outcome recorded: {result}")
    
    # Auto-record outcomes
    auto_result = await client.record_outcomes_auto(
        value=1000.0,
        currency="USD",
        details={"contract_value": 1000.0},
        verified=True
    )
    print(f"Auto-recorded outcomes: {auto_result}")
    
    # Use smart tracking for outcome-based model
    smart_result = await client.smart_track(
        value=750.0,
        metadata={"deal_type": "enterprise"}
    )
    print(f"Smart tracked outcomes: {smart_result}")


# Example 5: Workflow-Based Billing Model
async def example_workflow_based_billing():
    """Example for workflow-based billing model."""
    client = example_basic_setup()
    
    print("=== Workflow-Based Billing Example ===")
    
    # Get supported workflows
    workflows = await client.get_supported_workflows()
    print(f"Supported workflows: {workflows}")
    
    # Record single workflow
    if workflows:
        workflow_type = workflows[0]["type"]
        result = await client.record_workflow(
            workflow_type=workflow_type,
            metadata={"customer_id": "C456", "complexity": "medium"}
        )
        print(f"Workflow recorded: {result}")
    
    # Record bulk workflows
    workflow_executions = {
        "lead_research": 10,
        "email_personalization": 25,
        "follow_up_scheduling": 15
    }
    
    # Validate workflow data first
    validation = await client.validate_workflow_data(workflow_executions)
    print(f"Workflow validation: {validation}")
    
    if validation.get("valid", False):
        # Record bulk workflows
        bulk_result = await client.record_bulk_workflows(
            workflow_executions=workflow_executions,
            commitment_exceeded=False
        )
        print(f"Bulk workflows recorded: {bulk_result}")
    
    # Use smart tracking for workflow-based model
    smart_result = await client.smart_track(
        workflow_type="lead_research",
        metadata={"industry": "technology"}
    )
    print(f"Smart tracked workflow: {smart_result}")


# Example 6: Hybrid Billing Model
async def example_hybrid_billing():
    """Example for hybrid billing model."""
    client = example_basic_setup()
    
    print("=== Hybrid Billing Example ===")
    
    # Get supported activities and outcomes
    activities = await client.get_supported_activities()
    outcomes = await client.get_supported_outcomes()
    
    print(f"Supported activities: {activities}")
    print(f"Supported outcomes: {outcomes}")
    
    # Use smart tracking for hybrid model
    smart_result = await client.smart_track(
        activity_units=3,
        value=1500.0,
        metadata={"campaign_id": "C789", "client": "Big Corp"}
    )
    print(f"Smart tracked hybrid: {smart_result}")
    
    # Track multiple metrics at once
    activities_data = [{"type": activities[0], "metadata": {"batch": "B001"}}] if activities else []
    outcomes_data = [{"type": outcomes[0], "value": 2000.0, "currency": "USD"}] if outcomes else []
    
    metrics_result = await client.track_agent_metrics(
        activities=activities_data,
        costs=[
            {"amount": 10.50, "type": "compute", "currency": "USD"}
        ],
        outcomes=outcomes_data
    )
    print(f"Multiple metrics tracked: {metrics_result}")


# Example 7: Cost Tracking and Estimation
async def example_cost_tracking():
    """Example for cost tracking and estimation."""
    client = example_basic_setup()
    
    print("=== Cost Tracking Example ===")
    
    # Record different types of costs
    costs = [
        {"amount": 5.50, "type": "compute", "details": {"instance_type": "m5.large"}},
        {"amount": 0.002, "type": "token", "details": {"tokens": 1000}},
        {"amount": 0.10, "type": "api_call", "details": {"service": "openai"}},
        {"amount": 2.00, "type": "storage", "details": {"gb_hours": 10}},
    ]
    
    for cost in costs:
        result = await client.record_cost(
            amount=cost["amount"],
            cost_type=cost["type"],
            currency="USD",
            details=cost["details"]
        )
        print(f"Cost recorded: {cost['type']} - ${cost['amount']}")
    
    # Cost estimation examples
    estimates = [
        {"activity_units": 10},
        {"outcome_value": 1000.0},
        {"workflow_executions": {"lead_research": 5, "email_personalization": 10}}
    ]
    
    for estimate_params in estimates:
        estimate = await client.estimate_cost(**estimate_params)
        print(f"Cost estimate for {estimate_params}: {estimate}")


# Example 8: Analytics and Reporting
async def example_analytics():
    """Example for analytics and reporting."""
    client = example_basic_setup()
    
    print("=== Analytics Example ===")
    
    # Get comprehensive agent stats
    stats = await client.get_agent_stats()
    print(f"Agent stats: {stats}")
    
    # Get billing summary with date range
    start_date = "2024-01-01T00:00:00Z"
    end_date = "2024-12-31T23:59:59Z"
    
    billing_summary = await client.get_billing_summary(
        start_date=start_date,
        end_date=end_date
    )
    print(f"Billing summary: {billing_summary}")
    
    # Get detailed billing configuration
    billing_config = await client.get_billing_config()
    print(f"Billing config: {billing_config}")


# Example 9: Error Handling and Validation
async def example_error_handling():
    """Example for proper error handling."""
    client = example_basic_setup()
    
    print("=== Error Handling Example ===")
    
    try:
        # This will fail if the workflow type is not supported
        await client.record_workflow(
            workflow_type="unsupported_workflow",
            metadata={"test": True}
        )
    except Exception as e:
        print(f"Expected error for unsupported workflow: {e}")
    
    try:
        # This will fail for outcome-based models if value is not provided
        await client.smart_track(metadata={"test": True})
    except Exception as e:
        print(f"Error for missing value in outcome model: {e}")
    
    # Validate workflow data before recording
    invalid_workflows = {"invalid_workflow": 5}
    validation = await client.validate_workflow_data(invalid_workflows)
    print(f"Validation result for invalid workflows: {validation}")


# Example 10: Simple Usage Patterns
async def example_simple_usage():
    """Example for simple usage patterns."""
    client = example_basic_setup()
    
    print("=== Simple Usage Example ===")
    
    # Simple tracking - works with any billing model
    result1 = await client.simple_track(
        value=500.0,
        metadata={"source": "api", "user_id": "U123"}
    )
    print(f"Simple track 1: {result1}")
    
    # Simple tracking with workflow
    result2 = await client.simple_track(
        workflow_type="lead_research",
        metadata={"industry": "finance"}
    )
    print(f"Simple track 2: {result2}")
    
    # Simple tracking with activity units
    result3 = await client.simple_track(
        activity_units=5,
        metadata={"batch_id": "B456"}
    )
    print(f"Simple track 3: {result3}")


# Example 11: AI Agent Integration
async def example_ai_agent_integration():
    """Example for AI agent integration - similar to the azure_agent.py example."""
    client = example_basic_setup()
    
    print("=== AI Agent Integration Example ===")
    
    # Simulate an AI agent processing requests
    requests = [
        {"id": "req_1", "type": "question_answering", "complexity": "low"},
        {"id": "req_2", "type": "code_generation", "complexity": "medium"},
        {"id": "req_3", "type": "data_analysis", "complexity": "high"},
    ]
    
    for request in requests:
        print(f"Processing request: {request['id']}")
        
        # Record the processing activity
        await client.record_activity(
            activity_type="request_processing",
            metadata={
                "request_id": request["id"],
                "request_type": request["type"],
                "complexity": request["complexity"]
            }
        )
        
        # Simulate some cost based on complexity
        cost_multiplier = {"low": 0.01, "medium": 0.05, "high": 0.10}
        cost = cost_multiplier.get(request["complexity"], 0.05)
        
        await client.record_cost(
            amount=cost,
            cost_type="compute",
            currency="USD",
            details={"request_id": request["id"]}
        )
        
        # Record outcome if successful
        if request["complexity"] != "high":  # Simulate some failures on high complexity
            await client.record_outcome(
                outcome_type="successful_completion",
                value=10.0,  # Value of successful completion
                currency="USD",
                details={"request_id": request["id"]},
                verified=True
            )
            print(f"✓ Request {request['id']} completed successfully")
        else:
            print(f"✗ Request {request['id']} failed")


# Main execution examples
async def run_examples():
    """Run all examples."""
    print("Xyra Client SDK Examples")
    print("=" * 50)
    
    examples = [
        ("Basic Setup", lambda: print("Client setup completed")),
        ("Agent-Based Billing", example_agent_based_billing),
        ("Activity-Based Billing", example_activity_based_billing),
        ("Outcome-Based Billing", example_outcome_based_billing),
        ("Workflow-Based Billing", example_workflow_based_billing),
        ("Hybrid Billing", example_hybrid_billing),
        ("Cost Tracking", example_cost_tracking),
        ("Analytics", example_analytics),
        ("Error Handling", example_error_handling),
        ("Simple Usage", example_simple_usage),
        ("AI Agent Integration", example_ai_agent_integration),
    ]
    
    for name, example_func in examples:
        try:
            print(f"\n{name}")
            print("-" * len(name))
            if asyncio.iscoroutinefunction(example_func):
                await example_func()
            else:
                example_func()
        except Exception as e:
            print(f"Example '{name}' failed: {e}")
        
        print()  # Add spacing between examples


# Quick Start Example
async def quick_start():
    """Quick start example for new users."""
    print("=== Quick Start Example ===")
    
    # 1. Set up the client
    client = XyraClient(
        base_url="http://localhost:8000",  # Replace with your Xyra API URL
        agent_id=1,  # Replace with your agent ID
        token="your-token-here"  # Replace with your API token
    )
    
    # 2. Check if everything is working
    health = await client.health_check()
    print(f"Health check: {health['status']}")
    
    if health['status'] != 'healthy':
        print("⚠️  Setup issues detected:")
        for warning in health.get('warnings', []):
            print(f"   - {warning}")
        return
    
    # 3. Use smart tracking (works with any billing model)
    result = await client.smart_track(
        value=100.0,  # For outcome-based models
        activity_units=1,  # For activity-based models
        workflow_type="default",  # For workflow-based models
        metadata={"user_id": "demo_user"}
    )
    
    print(f"✓ Tracking completed: {result}")
    
    # 4. Get agent statistics
    stats = await client.get_agent_stats()
    print(f"Agent stats: {stats}")


if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Quick Start")
    print("2. All Examples")
    print("3. Specific Example (modify the code)")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(quick_start())
    elif choice == "2":
        asyncio.run(run_examples())
    else:
        print("Modify the code to run specific examples")
        # Example: asyncio.run(example_activity_based_billing())
