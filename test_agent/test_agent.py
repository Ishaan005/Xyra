from xyra_client import XyraClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

xyra_client = XyraClient(
    base_url=os.getenv("XYRA_BASE_URL", "http://localhost:8000"),
    token=os.getenv("XYRA_TOKEN") or "",  # Token from environment variable with fallback
    agent_id=int(os.getenv("XYRA_AGENT_ID", "3")),
)

## Insert your Agent Functions here
async def main():
    # Check health first
    health = await xyra_client.health_check()
    print(f"Health check: {health}")
    
    # Use smart tracking (works with any billing model)
    await xyra_client.smart_track(metadata={"test": "simple_test"})
    
    # Record specific cost
    await xyra_client.record_cost(amount=0.05, cost_type="token", currency="USD")
    
    # Get stats
    stats = await xyra_client.get_agent_stats()
    print(f"Agent stats: {stats}")

# Start the app
if __name__ == "__main__":
    asyncio.run(main())