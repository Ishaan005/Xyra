from xyra_client import XyraClient
import asyncio

xyra_client = XyraClient(
    base_url="http://localhost:8000",  # Replace with your actual base URL
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY5OTIzNjgsInN1YiI6IjEifQ.rlqGBkrZRo_N3g9Chs1SFOVErfBpxEVB8Jqc99tnsHA",
    agent_id=3,
)

## Insert your Agent Functions here
async def main():
    #await xyra_client.record_activity()
    await xyra_client.record_cost(amount = 0.05, cost_type="token", currency="USD")

# Start the app
if __name__ == "__main__":
    asyncio.run(main())