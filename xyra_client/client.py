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

    async def _get(self, path: str) -> Dict[str, Any]:
        """
        Internal helper to send GET requests to the Xyra API.
        """
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def record_activity(self, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Record configured activities for the agent automatically.
        Fetches the agent's billing model, retrieves its ActivityBasedConfig entries,
        and posts an activity event for each configured action_type.
        """
        # Fetch agent to get billing_model_id
        agent = await self._get(f"/api/v1/agents/{self.agent_id}")
        bm_id = agent.get("billing_model_id")
        if not bm_id:
            raise ValueError("Agent has no billing_model_id assigned")
        
        # Fetch billing model to get activity_config list
        bm = await self._get(f"/api/v1/billing-models/{bm_id}")
        model_type = bm.get("model_type")
        configs = []

        if model_type == "activity":
            configs = bm.get("activity_config") or []
        elif model_type == "hybrid":
            hybrid_config_data = bm.get("hybrid_config")
            if hybrid_config_data:
                configs = hybrid_config_data.get("activity_configs") or []
        
        if not configs:
            raise ValueError(f"No applicable activity configurations found for billing model type '{model_type}'")
        
        results = []
        for cfg in configs:
            activity_type = cfg.get("activity_type")  # Updated from action_type to activity_type
            payload = {
                'agent_id': self.agent_id,
                'activity_type': activity_type,
                'activity_metadata': metadata or {}
            }
            results.append(await self._post(f"/api/v1/agents/{self.agent_id}/activities", payload))
        # Return single or list based on number of configs
        return results[0] if len(results) == 1 else results

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

    async def record_outcome(self, value: float, currency: str = 'USD', details: Optional[Dict[str, Any]] = None, verified: bool = True) -> Any:
        """
        Record outcome for the agent automatically based on billing model config.
        The server will compute cost and store outcome entries for each configured outcome_type.
        """
        # Fetch agent and billing model
        agent = await self._get(f"/api/v1/agents/{self.agent_id}")
        bm_id = agent.get("billing_model_id")
        if not bm_id:
            raise ValueError("Agent has no billing model assigned")
        
        bm = await self._get(f"/api/v1/billing-models/{bm_id}")
        model_type = bm.get("model_type")
        configs = []

        if model_type == "outcome":
            configs = bm.get("outcome_config") or []
        elif model_type == "hybrid":
            hybrid_config_data = bm.get("hybrid_config")
            if hybrid_config_data:
                configs = hybrid_config_data.get("outcome_configs") or []

        if not configs:
            raise ValueError(f"No applicable outcome configurations found for billing model type '{model_type}'")
        
        results = []
        for cfg in configs:
            payload = {
                'agent_id': self.agent_id,
                'outcome_type': cfg.get('outcome_type'),
                'value': value,
                'currency': currency,
                'details': details or {},
                'verified': verified
            }
            results.append(await self._post(f"/api/v1/agents/{self.agent_id}/outcomes", payload))
        return results[0] if len(results) == 1 else results

    async def record_workflow(self, workflow_type: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Record workflow execution for the agent automatically based on billing model config.
        """
        # Fetch agent and billing model
        agent = await self._get(f"/api/v1/agents/{self.agent_id}")
        bm_id = agent.get("billing_model_id")
        if not bm_id:
            raise ValueError("Agent has no billing model assigned")
        
        bm = await self._get(f"/api/v1/billing-models/{bm_id}")
        model_type = bm.get("model_type")
        
        if model_type != "workflow":
            raise ValueError(f"Agent billing model type '{model_type}' does not support workflow recording")
        
        workflow_types = bm.get("workflow_types") or []
        if not workflow_types:
            raise ValueError("No workflow types configured for this billing model")
        
        # Find matching workflow type
        matching_workflow = None
        for wt in workflow_types:
            if wt.get("workflow_type") == workflow_type:
                matching_workflow = wt
                break
        
        if not matching_workflow:
            raise ValueError(f"Workflow type '{workflow_type}' not found in billing model configuration")
        
        # Record workflow cost directly via agent service
        payload = {
            'agent_id': self.agent_id,
            'cost_type': 'workflow',
            'amount': matching_workflow.get('price_per_workflow', 0),
            'currency': bm.get('workflow_config', {}).get('currency', 'USD'),
            'details': {
                'workflow_type': workflow_type,
                'workflow_name': matching_workflow.get('workflow_name'),
                'metadata': metadata or {}
            }
        }
        return await self._post(f"/api/v1/agents/{self.agent_id}/costs", payload)
