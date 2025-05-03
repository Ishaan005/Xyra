from xyra_client import XyraClient

xyra_client = XyraClient(
    base_url="http://localhost:8000",  # Replace with your actual base URL
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDY5ODM4NTgsInN1YiI6IjEifQ.fvMRBNfok396yBSc0Hrk8VrB3zdtLWsn80VC1qzPo9E",
    agent_id="2",
)

## Insert your Agent Functions here

xyra_client.record_activity()