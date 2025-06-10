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
    #await xyra_client.record_activity()
    await xyra_client.record_cost(amount = 0.05, cost_type="token", currency="USD")

# Start the app
if __name__ == "__main__":
    asyncio.run(main())