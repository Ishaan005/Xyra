# API Keys Guide for Xyra Client SDK

This guide shows you how to create and use API keys with the Xyra Client SDK.

## API Key Concepts

API keys in Xyra are **organization-scoped** with **user ownership**:

- **Organization-scoped**: API keys belong to an organization and provide access to that organization's data
- **User ownership**: Each API key has an owner (the user who created it) for auditing and management
- **Organization visibility**: All users in an organization can see organization API keys via the "Show all organization keys" toggle
- **Access control**: Users can only modify API keys they created (except for organization admins)
- **Secure authentication**: API keys work with all Xyra API endpoints and provide the same access level as the owning user

## Access Levels

### My API Keys View (Default)
- Shows only API keys you have created
- You can create, modify, and delete these keys
- Suitable for personal/individual use

### All Organization Keys View
- Shows all API keys created by anyone in your organization
- Displays the owner (creator) of each key
- You can only modify keys you created
- Useful for organization administrators and key auditing

## Creating API Keys

### Via Frontend (Settings Page)

1. Navigate to the Settings page in the Xyra frontend
2. Go to the "API Keys" tab
3. Click "Create API Key"
4. Enter a name and optional description for your API key
5. Click "Create API Key"
6. **Important**: Copy the full API key immediately - you won't be able to see it again!

**Note**: The API key will be associated with your organization and you will be listed as the owner.

### Via API (Programmatic)

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Production API Key",
    "description": "API key for production environment"
  }'
```

**Note**: You must belong to an organization to create API keys via the API.

### List Organization API Keys

```bash
# List your own API keys
curl -X GET "http://localhost:8000/api/v1/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# List all API keys in your organization
curl -X GET "http://localhost:8000/api/v1/api-keys/organization/all" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Using API Keys with Xyra Client SDK

### Python SDK

```python
import asyncio
from xyra_client import XyraClient

async def main():
    # Initialize the client with your API key
    client = XyraClient(
        base_url="http://localhost:8000",
        agent_id=1,  # Your agent ID
        token="xyra_abc123..."  # Your API key (starts with xyra_)
    )
    
    # Check health
    health = await client.health_check()
    print(f"Status: {health['status']}")
    
    # Smart tracking - works with any billing model
    result = await client.smart_track(
        value=100.0,
        activity_units=1,
        workflow_type="default",
        metadata={"user_id": "demo_user"}
    )
    
    print(f"Tracking result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Environment Variables

Set your API key as an environment variable:

```bash
export XYRA_TOKEN="xyra_abc123..."
export XYRA_BASE_URL="http://localhost:8000"
export XYRA_AGENT_ID="1"
```

Then in your Python code:

```python
import os
from xyra_client import XyraClient

client = XyraClient(
    base_url=os.getenv("XYRA_BASE_URL"),
    agent_id=int(os.getenv("XYRA_AGENT_ID")),
    token=os.getenv("XYRA_TOKEN")
)
```

## API Key Features

### Format
- API keys have the format: `xyra_<random-string>`
- Example: `xyra_abc123def456ghi789jkl012`

### Security
- API keys are hashed and stored securely in the database
- Only the prefix is shown in the UI for identification
- Full keys are only shown once during creation

### Management
- View all your organization's API keys in the Settings page
- See when keys were created, who created them, and when they were last used
- Deactivate or delete keys as needed (if you're the owner)
- Set expiration dates (optional)
- Organization members can see all API keys but can only modify keys they created

### Authentication
- API keys work with all Xyra API endpoints
- Include in the Authorization header: `Bearer xyra_abc123...`
- Can be used instead of JWT tokens for programmatic access

## Best Practices

1. **Keep API Keys Secret**: Never commit API keys to version control
2. **Use Environment Variables**: Store keys in environment variables or secure config
3. **Rotate Keys Regularly**: Create new keys and delete old ones periodically
4. **Use Descriptive Names**: Name your keys to identify their purpose
5. **Monitor Usage**: Check the "last used" timestamp to identify unused keys
6. **Limit Scope**: Create separate keys for different environments (dev, staging, prod)

## Troubleshooting

### Invalid API Key Format
Make sure your API key starts with `xyra_`. Example:
```
✓ xyra_abc123def456ghi789jkl012
✗ abc123def456ghi789jkl012
```

### 401 Unauthorized
- Check that your API key is correct and hasn't been deleted
- Verify the key is active (not expired or deactivated)
- Ensure you're using the correct Authorization header format
- Confirm your user account is active and belongs to an organization

### Organization Access Issues
- Verify you belong to an organization (API keys require organization membership)
- Check that the API key belongs to your organization
- Ensure the API key owner is still an active member of the organization

### Agent Not Found
- Verify the agent_id exists and belongs to your organization
- Check that your user has access to the specified agent

## Example Use Cases

### Organization CI/CD Pipeline
```bash
# Organization-wide CI/CD pipeline
# API key provides access to all agents in the organization
export XYRA_TOKEN="xyra_ci_cd_key_here"
export XYRA_AGENT_ID="1"  # Any agent in your organization
python deploy_agent.py
```

### Multi-Agent Monitoring Script
```python
# Monitor multiple agents in your organization
import asyncio
from xyra_client import XyraClient

async def monitor_organization_agents():
    # API key provides access to all organization agents
    client = XyraClient(
        base_url=os.getenv("XYRA_BASE_URL"),
        agent_id=int(os.getenv("XYRA_AGENT_ID")),  
        token=os.getenv("XYRA_TOKEN")  # Organization API key
    )
    
    # Monitor any agent in your organization
    for agent_id in [1, 2, 3]:  # Your organization's agents
        client.agent_id = agent_id
        stats = await client.get_agent_stats()
        print(f"Agent {agent_id} status: {stats}")
```

### Team Development Environment
```python
# Shared API key for development team
# All developers can use the same organization API key
# to access development agents and resources
    
    stats = await client.get_agent_stats()
    if stats['error_rate'] > 0.05:  # 5% error rate
        # Send alert
        print("High error rate detected!")
```

### Batch Processing
```python
# Process multiple records
for record in batch_records:
    await client.record_activity("process_record", {
        "record_id": record.id,
        "size": record.size
    })
```
