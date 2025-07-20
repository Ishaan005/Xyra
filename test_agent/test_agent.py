import sys
import os
# Add parent directory to Python path to find xyra_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xyra_client import XyraClient
import asyncio
from dotenv import load_dotenv

load_dotenv()

xyra_client = XyraClient(
    base_url=os.getenv("XYRA_BASE_URL", "http://localhost:8000"),
    token=os.getenv("XYRA_TOKEN") or "",  # Token from environment variable with fallback
    agent_id=int(os.getenv("XYRA_AGENT_ID", "16")),
)

async def main():
    # Check health
    health = await xyra_client.health_check()
    print(f"Health check: {health}")

    # Record a single outcome (simulate a successful outcome for ADO Automation)
    result = await xyra_client.record_outcome(
        outcome_type="time_savings",  # Use the actual outcome type configured for your agent
        value=0.69,  # Value is arbitrary for fixed charge, can be 1
        currency="EUR",
        verified=True,
        outcome_count=1  # One successful outcome
    )
    print(f"Outcome recorded: {result}")

if __name__ == "__main__":
    asyncio.run(main())