import httpx
from typing import Any, Dict, Optional


class XyraClient:
    """
    Python SDK for interacting with the Xyra API.

    Attributes:
        base_url: Base URL of the Xyra API (no trailing slash).
        agent_id: ID of the agent for which to record activities, costs, and outcomes.
    """

    def __init__(self, base_url: str, agent_id: int, token: str) -> None:
        """
        Initialize the XyraClient.

        Args:
            base_url: Base URL of the Xyra API.
            agent_id: Agent ID for namespaced operations.
            token: Bearer token for authentication.
        """
        self.base_url = base_url.rstrip('/')
        self.agent_id = agent_id
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal helper to send POST requests to the Xyra API.
        """
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def record_activity(self, activity_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record an activity for the agent.

        Args:
            activity_type: Type of the activity (e.g. "file_processed").
            metadata: Arbitrary metadata about the activity.
        """
        path = f"/api/v1/agents/{self.agent_id}/activities"
        payload = {
            'agent_id': self.agent_id,
            'activity_type': activity_type,
            'activity_metadata': metadata or {}
        }
        return await self._post(path, payload)

    async def record_cost(self, amount: float, cost_type: str , currency: str) -> Dict[str, Any]:
        """
        Record a cost for the agent.

        Args:
            amount: Numeric cost amount.
            cost_type: Type of cost (default "token").
            currency: Currency code (default "USD").
        """
        path = f"/api/v1/agents/{self.agent_id}/costs"
        payload = {
            'agent_id': self.agent_id,
            'cost_type': cost_type,
            'amount': amount,
            'currency': currency,
            'details': {}
        }
        return await self._post(path, payload)

    async def record_outcome(
        self,
        outcome_type: str,
        value: float,
        currency: str,  
        details: Optional[Dict[str, Any]] = None,
        verified: bool = True
    ) -> Dict[str, Any]:
        """
        Record an outcome for the agent.

        Args:
            outcome_type: Type classification of the outcome.
            value: Numeric value of the outcome.
            currency: Currency code (default "USD").
            details: Additional details (default empty dict).
            verified: Whether the outcome is verified (default True).
        """
        path = f"/api/v1/agents/{self.agent_id}/outcomes"
        payload = {
            'agent_id': self.agent_id,
            'outcome_type': outcome_type,
            'value': value,
            'currency': currency,
            'details': details or {},
            'verified': verified
        }
        return await self._post(path, payload)
