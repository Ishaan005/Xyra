# Xyra Client SDK

A Python SDK for interacting with the Xyra API to track agent metrics including activities, costs, outcomes, and workflows across different billing models.

## Installation

```bash
# Install from source
cd xyra_client
pip install -e .

# Or install specific requirements
pip install httpx>=0.23.0
```

## Quick Start

```python
import asyncio
from xyra_client import XyraClient

async def main():
    # Initialize the client
    client = XyraClient(
        base_url="http://localhost:8000",  # Your Xyra API URL
        agent_id=1,  # Your agent ID
        token="your-token-here"  # Your API token
    )
    
    # Check health
    health = await client.health_check()
    print(f"Status: {health['status']}")
    
    # Smart tracking - works with any billing model
    result = await client.smart_track(
        value=100.0,  # For outcome-based models
        activity_units=1,  # For activity-based models
        workflow_type="default",  # For workflow-based models
        metadata={"user_id": "demo_user"}
    )
    
    print(f"Tracking result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

### 🎯 **Smart Tracking**
- Automatic billing model detection
- Intelligent parameter mapping
- Single method works across all billing models

### 🔄 **Multiple Billing Models**
- **Agent-based**: Track agent usage and fees
- **Activity-based**: Track specific activities and units
- **Outcome-based**: Track outcomes and value generation
- **Workflow-based**: Track workflow executions

### 📊 **Comprehensive Analytics**
- Real-time cost tracking
- Billing summaries and breakdowns
- Agent performance statistics
- Cost estimation and validation

### 🛠️ **Developer-Friendly**
- Type hints for better IDE support
- Comprehensive error handling
- Detailed documentation and examples
- Health checks and validation

## Billing Models

### Agent-Based Billing

```python
# Track agent usage
result = await client.smart_track(
    metadata={"session_id": "session_123"}
)

# Or manually record costs
await client.record_cost(
    amount=5.0,
    cost_type="agent",
    details={"agents": 1}
)
```

### Activity-Based Billing

```python
# Get supported activities
activities = await client.get_supported_activities()

# Record specific activity
await client.record_activity(
    activity_type="data_processing",
    metadata={"records": 1000}
)

# Auto-record all configured activities
await client.record_activities_auto(
    metadata={"batch_id": "batch_123"}
)

# Smart tracking for activities
await client.smart_track(
    activity_units=5,
    metadata={"operation": "data_processing"}
)
```

### Outcome-Based Billing

```python
# Get supported outcomes
outcomes = await client.get_supported_outcomes()

# Record specific outcome
await client.record_outcome(
    outcome_type="sale",
    value=500.0,
    currency="USD",
    details={"deal_id": "D123"},
    verified=True
)

# Auto-record outcomes
await client.record_outcomes_auto(
    value=1000.0,
    currency="USD",
    details={"contract_value": 1000.0}
)

# Smart tracking for outcomes
await client.smart_track(
    value=750.0,
    metadata={"deal_type": "enterprise"}
)
```

### Workflow-Based Billing

```python
# Get supported workflows
workflows = await client.get_supported_workflows()

# Record single workflow
await client.record_workflow(
    workflow_type="lead_research",
    metadata={"industry": "tech"}
)

# Record bulk workflows
await client.record_bulk_workflows(
    workflow_executions={
        "lead_research": 10,
        "email_personalization": 25
    },
    commitment_exceeded=False
)

# Validate workflow data
validation = await client.validate_workflow_data({
    "lead_research": 5,
    "email_personalization": 10
})

# Smart tracking for workflows
await client.smart_track(
    workflow_type="lead_research",
    metadata={"industry": "technology"}
)
```

## Core Methods

### Information Methods

```python
# Get agent information
agent_info = await client.get_agent_info()

# Get billing configuration
billing_config = await client.get_billing_config()

# Get billing summary
summary = await client.get_billing_summary(
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-12-31T23:59:59Z"
)

# Get agent statistics
stats = await client.get_agent_stats()

# Get billing model info
model_info = await client.get_billing_model_info()
```

### Recording Methods

```python
# Record activity
await client.record_activity("data_processing", {"records": 1000})

# Record cost
await client.record_cost(10.50, "compute", "USD", {"instance": "m5.large"})

# Record outcome
await client.record_outcome("sale", 500.0, "USD", {"deal_id": "D123"})

# Record workflow
await client.record_workflow("lead_research", {"industry": "tech"})
```

### Utility Methods

```python
# Health check
health = await client.health_check()

# Cost estimation
estimate = await client.estimate_cost(
    activity_units=10,
    outcome_value=1000.0
)

# Simple tracking (works with any model)
await client.simple_track(
    value=500.0,
    workflow_type="lead_research",
    metadata={"source": "api"}
)
```

## Configuration

### Environment Variables

```bash
# Set these in your environment or .env file
export XYRA_BASE_URL="http://localhost:8000"
export XYRA_AGENT_ID="1"
export XYRA_TOKEN="your-token-here"
```

### Client Initialization

```python
import os
from xyra_client import XyraClient

# From environment variables
client = XyraClient(
    base_url=os.getenv("XYRA_BASE_URL", "http://localhost:8000"),
    agent_id=int(os.getenv("XYRA_AGENT_ID", "1")),
    token=os.getenv("XYRA_TOKEN", "your-token-here")
)

# Direct initialization
client = XyraClient(
    base_url="https://api.xyra.com",
    agent_id=123,
    token="your-api-token"
)
```

## Error Handling

```python
import asyncio
from xyra_client import XyraClient

async def safe_tracking():
    client = XyraClient(base_url="...", agent_id=1, token="...")
    
    try:
        # Check health first
        health = await client.health_check()
        if health['status'] != 'healthy':
            print("Setup issues:", health.get('warnings', []))
            return
        
        # Perform tracking
        result = await client.smart_track(value=100.0)
        print("Success:", result)
        
    except Exception as e:
        print(f"Error: {e}")
        
        # Try to get more info
        try:
            agent_info = await client.get_agent_info()
            print("Agent exists:", agent_info.get('name'))
        except:
            print("Agent not found or authentication failed")
```

## Examples

See `examples.py` for comprehensive examples covering:

- All billing models
- Error handling
- Cost tracking and estimation
- Analytics and reporting
- AI agent integration
- Bulk operations

Run examples:

```bash
python examples.py
```

## API Reference

### XyraClient

#### Constructor
```python
XyraClient(base_url: str, agent_id: int, token: str)
```

#### Smart Tracking Methods
- `smart_track(**kwargs) -> Dict[str, Any]`
- `simple_track(**kwargs) -> Dict[str, Any]`

#### Recording Methods
- `record_activity(activity_type: str, metadata: Optional[Dict] = None) -> Dict[str, Any]`
- `record_cost(amount: float, cost_type: str = "custom", currency: str = "USD", details: Optional[Dict] = None) -> Dict[str, Any]`
- `record_outcome(outcome_type: str, value: float, currency: str = "USD", details: Optional[Dict] = None, verified: bool = True) -> Dict[str, Any]`
- `record_workflow(workflow_type: str, metadata: Optional[Dict] = None) -> Dict[str, Any]`
- `record_bulk_workflows(workflow_executions: Dict[str, int], commitment_exceeded: bool = False) -> Dict[str, Any]`

#### Information Methods
- `get_agent_info() -> Dict[str, Any]`
- `get_billing_config() -> Dict[str, Any]`
- `get_billing_summary(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]`
- `get_agent_stats() -> Dict[str, Any]`
- `get_billing_model_info() -> Dict[str, Any]`

#### Utility Methods
- `health_check() -> Dict[str, Any]`
- `estimate_cost(**kwargs) -> Dict[str, Any]`
- `validate_workflow_data(workflow_executions: Dict[str, int]) -> Dict[str, Any]`

#### Support Methods
- `get_supported_activities() -> List[str]`
- `get_supported_outcomes() -> List[str]`
- `get_supported_workflows() -> List[Dict[str, Any]]`

## Common Use Cases

### 1. AI Agent Integration

```python
async def process_request(request_data):
    client = XyraClient(...)
    
    # Start processing
    await client.record_activity("request_processing", request_data)
    
    # ... do AI processing ...
    
    # Record costs
    await client.record_cost(compute_cost, "compute")
    
    # Record outcome if successful
    if success:
        await client.record_outcome("completion", value, metadata=result_data)
```

### 2. Batch Processing

```python
async def process_batch(batch_data):
    client = XyraClient(...)
    
    # Process multiple items
    for item in batch_data:
        await client.record_activity("item_processing", {"item_id": item.id})
    
    # Record bulk results
    await client.record_outcomes_auto(
        value=total_value,
        details={"batch_size": len(batch_data)}
    )
```

### 3. SaaS Application Integration

```python
async def handle_user_action(user_id, action_type, value=None):
    client = XyraClient(...)
    
    # Smart tracking adapts to your billing model
    await client.smart_track(
        value=value,
        activity_units=1,
        metadata={"user_id": user_id, "action": action_type}
    )
```

## Best Practices

1. **Always check health first** in production applications
2. **Use smart tracking** for maximum flexibility
3. **Include meaningful metadata** for better analytics
4. **Handle errors gracefully** with try-catch blocks
5. **Use environment variables** for configuration
6. **Validate workflow data** before bulk recording
7. **Monitor billing summaries** regularly

## Requirements

- Python 3.8+
- httpx>=0.23.0

## License

This SDK is part of the Xyra project and follows the same license terms.

## Support

For issues, questions, or contributions:
- Check the main Xyra repository
- Review the examples in `examples.py`
- Use the health check method for debugging
- Check agent configuration in the Xyra dashboard

## Changelog

### Version 0.1.0
- Initial release
- Support for all billing models
- Smart tracking functionality
- Comprehensive error handling
- Full API coverage
- Examples and documentation
