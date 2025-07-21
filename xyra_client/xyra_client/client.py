import httpx
from typing import Any, Dict, Optional, List, Union
from datetime import datetime


class XyraClient:
    """
    Python SDK for interacting with the Xyra API.
    
    This client provides an easy-to-use interface for tracking agent metrics including
    activities, costs, outcomes, and workflows across different billing models.

    Attributes:
        base_url: Base URL of the Xyra API (no trailing slash).
        agent_id: ID of the agent for which to record activities, costs, and outcomes.
        
    Example:
        >>> client = XyraClient("https://api.xyra.com", agent_id=123, token="your_token")
        >>> await client.record_activity("data_processing", {"records": 1000})
        >>> await client.record_cost(10.50, "compute", "USD")
        >>> await client.record_outcome(500.0, "USD", {"deal_closed": True})
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

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal helper to send GET requests to the Xyra API.
        """
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    # Agent Information Methods
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the current agent.
        
        Returns:
            Dictionary containing agent information including billing model details.
        """
        return await self._get(f"/api/v1/agents/{self.agent_id}")
    
    async def get_billing_config(self) -> Dict[str, Any]:
        """
        Get the billing configuration for the current agent.
        
        Returns:
            Dictionary containing billing model configuration including all active billing configs.
        """
        return await self._get(f"/api/v1/agents/{self.agent_id}/billing-config")
    
    async def get_billing_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a detailed billing summary for the current agent.
        
        Args:
            start_date: Optional start date filter (ISO format: "2024-01-01T00:00:00Z")
            end_date: Optional end date filter (ISO format: "2024-01-31T23:59:59Z")
            
        Returns:
            Dictionary containing detailed billing information with cost breakdowns.
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        return await self._get(f"/api/v1/agents/{self.agent_id}/billing-summary", params)

    # Enhanced Billing Information Methods
    
    async def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for the current agent.
        
        Returns:
            Dictionary containing activity count, total costs, outcomes, and margin calculations.
        """
        return await self._get(f"/api/v1/agents/{self.agent_id}/stats")
    
    async def get_supported_activities(self) -> List[str]:
        """
        Get list of activity types supported by the agent's billing model.
        
        Returns:
            List of activity type strings that can be used with record_activity().
        """
        try:
            config = await self.get_billing_config()
            activity_types = []
            
            if config.get("model_type") == "activity":
                configs = config.get("activity_configs", [])
                activity_types = [cfg.get("activity_type") for cfg in configs if cfg.get("is_active")]
            
            return [at for at in activity_types if at]
        except Exception:
            return []
    
    async def get_supported_outcomes(self) -> List[str]:
        """
        Get list of outcome types supported by the agent's billing model.
        
        Returns:
            List of outcome type strings that can be used with record_outcome().
        """
        try:
            config = await self.get_billing_config()
            outcome_types = []
            
            if config.get("model_type") == "outcome":
                configs = config.get("outcome_configs", [])
                outcome_types = [cfg.get("outcome_type") for cfg in configs if cfg.get("is_active")]
            
            return [ot for ot in outcome_types if ot]
        except Exception:
            return []
    
    async def get_supported_workflows(self) -> List[Dict[str, Any]]:
        """
        Get list of workflow types supported by the agent's billing model.
        
        Returns:
            List of workflow configuration dictionaries with type, name, and pricing info.
        """
        try:
            config = await self.get_billing_config()
            
            if config.get("model_type") == "workflow":
                workflow_types = config.get("workflow_types", [])
                return [
                    {
                        "type": wt.get("workflow_type"),
                        "name": wt.get("workflow_name"),
                        "price": wt.get("price_per_workflow"),
                        "complexity": wt.get("complexity_level"),
                        "description": wt.get("description"),
                        "active": wt.get("is_active", True)
                    }
                    for wt in workflow_types if wt.get("is_active", True)
                ]
            
            return []
        except Exception:
            return []

    # Activity Recording Methods

    async def record_activity(self, activity_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record a specific activity for the agent.
        
        This method allows you to record specific activity types rather than auto-recording
        all configured activities. Use this when you want fine-grained control over activity tracking.
        
        Args:
            activity_type: The type of activity to record (must match billing model config)
            metadata: Optional metadata to include with the activity
            
        Returns:
            Dictionary containing the recorded activity information.
            
        Example:
            >>> await client.record_activity("data_processing", {"records_processed": 1000})
        """
        payload = {
            'agent_id': self.agent_id,
            'activity_type': activity_type,
            'activity_metadata': metadata or {}
        }
        return await self._post(f"/api/v1/agents/{self.agent_id}/activities", payload)

    async def record_activities_auto(self, metadata: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Record configured activities for the agent automatically.
        
        This method fetches the agent's billing model, retrieves its activity configurations,
        and posts an activity event for each configured activity type.
        
        Args:
            metadata: Optional metadata to include with all activities
            
        Returns:
            Single activity dict if only one activity type configured,
            or list of activity dicts if multiple activity types configured.
            
        Example:
            >>> await client.record_activities_auto({"batch_id": "batch_123"})
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
        
        if not configs:
            raise ValueError(f"No applicable activity configurations found for billing model type '{model_type}'")
        
        results = []
        for cfg in configs:
            activity_type = cfg.get("activity_type")
            results.append(await self.record_activity(activity_type, metadata))
        
        return results[0] if len(results) == 1 else results

    # Cost Recording Methods

    async def record_cost(self, amount: float, cost_type: str = "custom", currency: str = "USD", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record a cost for the agent.

        Args:
            amount: Numeric cost amount.
            cost_type: Type of cost (e.g., "compute", "token", "api_call", "custom").
            currency: Currency code (default "USD").
            details: Optional additional details about the cost.
            
        Returns:
            Dictionary containing the recorded cost information.
            
        Example:
            >>> await client.record_cost(10.50, "compute", "USD", {"instance_type": "m5.large"})
        """
        payload = {
            'agent_id': self.agent_id,
            'cost_type': cost_type,
            'amount': amount,
            'currency': currency,
            'details': details or {}
        }
        return await self._post(f"/api/v1/agents/{self.agent_id}/costs", payload)

    # Outcome Recording Methods

    async def record_outcome(self, outcome_type: str, value: float, currency: str = 'USD', details: Optional[Dict[str, Any]] = None, verified: bool = True, outcome_count: int = 1) -> Dict[str, Any]:
        """
        Record a specific outcome for the agent.
        
        This method allows you to record specific outcome types rather than auto-recording
        all configured outcomes. Use this when you want fine-grained control over outcome tracking.
        
        Args:
            outcome_type: The type of outcome to record (must match billing model config)
            value: The value of the outcome
            currency: Currency code (default "USD")
            details: Optional additional details about the outcome
            verified: Whether the outcome is verified (default True)
            outcome_count: The number of outcomes to record (for fixed-charge billing)
            
        Returns:
            Dictionary containing the recorded outcome information.
            
        Example:
            >>> await client.record_outcome("sale", 500.0, "USD", {"deal_id": "D123"}, True)
        """
        payload = {
            'agent_id': self.agent_id,
            'outcome_type': outcome_type,
            'value': value,
            'currency': currency,
            'details': details or {},
            'verified': verified,
            'outcome_count': outcome_count
        }
        return await self._post(f"/api/v1/agents/{self.agent_id}/outcomes", payload)

    async def record_outcomes_auto(self, value: float, currency: str = 'USD', details: Optional[Dict[str, Any]] = None, verified: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Record outcome for the agent automatically based on billing model config.
        
        This method fetches the agent's billing model and records outcomes for each
        configured outcome type. The server will compute costs automatically.
        
        Args:
            value: The value of the outcome
            currency: Currency code (default "USD")
            details: Optional additional details about the outcome
            verified: Whether the outcome is verified (default True)
            
        Returns:
            Single outcome dict if only one outcome type configured,
            or list of outcome dicts if multiple outcome types configured.
            
        Example:
            >>> await client.record_outcomes_auto(500.0, "USD", {"deal_closed": True})
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

        if not configs:
            raise ValueError(f"No applicable outcome configurations found for billing model type '{model_type}'")
        
        results = []
        for cfg in configs:
            outcome_type = cfg.get('outcome_type')
            results.append(await self.record_outcome(outcome_type, value, currency, details, verified))
        
        return results[0] if len(results) == 1 else results

    # Workflow Recording Methods

    async def record_workflow(self, workflow_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record a single workflow execution for the agent.
        
        This method records a workflow execution and auto-calculates the cost based on
        the agent's billing model configuration. It uses the new workflow recording endpoint.
        
        Args:
            workflow_type: The type of workflow to record (must match billing model config)
            metadata: Optional metadata to include with the workflow execution
            
        Returns:
            Dictionary containing the recorded workflow cost information.
            
        Example:
            >>> await client.record_workflow("lead_research", {"target_industry": "tech"})
        """
        # Use the bulk workflow endpoint with a single workflow
        workflow_executions = {workflow_type: 1}
        result = await self.record_bulk_workflows(workflow_executions, commitment_exceeded=False)
        
        # Return the first cost entry from the bulk response
        if isinstance(result, dict) and 'cost_entries' in result:
            cost_entries = result['cost_entries']
            return cost_entries[0] if cost_entries else {}
        return result

    async def record_bulk_workflows(self, workflow_executions: Dict[str, int], commitment_exceeded: bool = False) -> Dict[str, Any]:
        """
        Record multiple workflow executions at once for the agent.
        
        This method is more efficient for recording multiple workflow executions
        and handles bulk pricing calculations correctly.
        
        Args:
            workflow_executions: Dictionary mapping workflow types to execution counts
            commitment_exceeded: Whether these executions exceed commitment tier limits
            
        Returns:
            Dictionary containing the list of recorded workflow cost entries.
            
        Example:
            >>> await client.record_bulk_workflows({
            ...     "lead_research": 10,
            ...     "email_personalization": 25
            ... }, commitment_exceeded=False)
        """
        payload = {
            'workflow_executions': workflow_executions,
            'commitment_exceeded': commitment_exceeded
        }
        return await self._post(f"/api/v1/agents/{self.agent_id}/workflows/bulk", payload)

    async def validate_workflow_data(self, workflow_executions: Dict[str, int]) -> Dict[str, Any]:
        """
        Validate workflow execution data against the agent's billing model.
        
        This method checks if the provided workflow types are configured for the agent
        and provides cost estimates without actually recording the workflows.
        
        Args:
            workflow_executions: Dictionary mapping workflow types to execution counts
            
        Returns:
            Dictionary containing validation results and cost estimates.
            
        Example:
            >>> validation = await client.validate_workflow_data({
            ...     "lead_research": 10,
            ...     "email_personalization": 25
            ... })
            >>> print(f"Valid: {validation['valid']}")
            >>> print(f"Estimated cost: ${validation['total_estimated_cost']}")
        """
        payload = {
            'workflow_executions': workflow_executions
        }
        return await self._post(f"/api/v1/agents/{self.agent_id}/workflows/validate", payload)

    # Convenience Methods
    
    async def track_agent_metrics(self, activities: Optional[List[Dict[str, Any]]] = None, 
                                costs: Optional[List[Dict[str, Any]]] = None,
                                outcomes: Optional[List[Dict[str, Any]]] = None,
                                workflows: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Track multiple types of agent metrics in a single call.
        
        This convenience method allows you to record multiple activities, costs, outcomes,
        and workflows in an efficient manner.
        
        Args:
            activities: List of activity dicts with 'type' and optional 'metadata' keys
            costs: List of cost dicts with 'amount', 'type', optional 'currency' and 'details' keys
            outcomes: List of outcome dicts with 'type', 'value', optional 'currency', 'details', 'verified' keys
            workflows: List of workflow dicts with 'type' and optional 'metadata' keys
            
        Returns:
            Dictionary containing results from all recorded metrics.
            
        Example:
            >>> results = await client.track_agent_metrics(
            ...     activities=[{"type": "data_processing", "metadata": {"records": 1000}}],
            ...     costs=[{"amount": 5.0, "type": "compute"}],
            ...     outcomes=[{"type": "sale", "value": 500.0}],
            ...     workflows=[{"type": "lead_research", "metadata": {"industry": "tech"}}]
            ... )
        """
        results = {
            'activities': [],
            'costs': [],
            'outcomes': [],
            'workflows': []
        }
        
        # Record activities
        if activities:
            for activity in activities:
                activity_type = activity.get('type')
                metadata = activity.get('metadata')
                if activity_type:
                    result = await self.record_activity(activity_type, metadata)
                    results['activities'].append(result)
        
        # Record costs
        if costs:
            for cost in costs:
                amount = cost.get('amount')
                cost_type = cost.get('type', 'custom')
                currency = cost.get('currency', 'USD')
                details = cost.get('details')
                if amount is not None:
                    result = await self.record_cost(amount, cost_type, currency, details)
                    results['costs'].append(result)
        
        # Record outcomes
        if outcomes:
            for outcome in outcomes:
                outcome_type = outcome.get('type')
                value = outcome.get('value')
                currency = outcome.get('currency', 'USD')
                details = outcome.get('details')
                verified = outcome.get('verified', True)
                if outcome_type and value is not None:
                    result = await self.record_outcome(outcome_type, value, currency, details, verified)
                    results['outcomes'].append(result)
        
        # Record workflows
        if workflows:
            for workflow in workflows:
                workflow_type = workflow.get('type')
                metadata = workflow.get('metadata')
                if workflow_type:
                    result = await self.record_workflow(workflow_type, metadata)
                    results['workflows'].append(result)
        
        return results

    # Smart Auto-Recording Methods
    
    async def smart_track(self, value: Optional[float] = None, 
                         metadata: Optional[Dict[str, Any]] = None,
                         activity_units: int = 1,
                         outcome_type: Optional[str] = None,
                         workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Intelligently track metrics based on the agent's billing model type.
        
        This method automatically determines what to record based on the billing model:
        - Agent-based: Records agent usage
        - Activity-based: Records configured activities
        - Outcome-based: Records outcomes (requires value)
        - Workflow-based: Records workflow execution (requires workflow_type)
        
        Args:
            value: Value for outcome recording (required for outcome-based models)
            metadata: Optional metadata to include with recordings
            activity_units: Number of activity units to record (default 1)
            outcome_type: Specific outcome type to record (auto-detected if not provided)
            workflow_type: Specific workflow type to record (required for workflow models)
            
        Returns:
            Dictionary containing all recorded metrics and their results.
            
        Example:
            >>> # For outcome-based model
            >>> results = await client.smart_track(value=500.0, metadata={"deal_id": "D123"})
            
            >>> # For workflow-based model  
            >>> results = await client.smart_track(workflow_type="lead_research", metadata={"industry": "tech"})
            
            >>> # For activity-based model
            >>> results = await client.smart_track(activity_units=5, metadata={"batch_id": "B456"})
        """
        try:
            config = await self.get_billing_config()
            model_type = config.get("model_type")
            results = {
                "model_type": model_type,
                "activities": [],
                "costs": [],
                "outcomes": [],
                "workflows": []
            }
            
            if model_type == "agent":
                # For agent-based billing, record a usage event
                cost_result = await self.record_cost(
                    amount=0,  # Amount will be calculated by server
                    cost_type="agent",
                    details={
                        "agents": 1,
                        "metadata": metadata or {}
                    }
                )
                results["costs"].append(cost_result)
                
            elif model_type == "activity":
                # Record all configured activities
                activity_types = await self.get_supported_activities()
                for activity_type in activity_types:
                    for _ in range(activity_units):
                        activity_result = await self.record_activity(activity_type, metadata)
                        results["activities"].append(activity_result)
                        
            elif model_type == "outcome":
                if value is None:
                    raise ValueError("value parameter is required for outcome-based billing models")
                
                # Record outcome for specified type or first configured type
                if outcome_type:
                    outcome_result = await self.record_outcome(outcome_type, value, details=metadata)
                    results["outcomes"].append(outcome_result)
                else:
                    # Auto-record for all configured outcome types
                    outcome_types = await self.get_supported_outcomes()
                    for ot in outcome_types:
                        outcome_result = await self.record_outcome(ot, value, details=metadata)
                        results["outcomes"].append(outcome_result)
                        
            elif model_type == "workflow":
                if workflow_type is None:
                    raise ValueError("workflow_type parameter is required for workflow-based billing models")
                
                workflow_result = await self.record_workflow(workflow_type, metadata)
                results["workflows"].append(workflow_result)
            
            return results
            
        except Exception as e:
            raise ValueError(f"Smart tracking failed: {str(e)}")
    
    async def simple_track(self, **kwargs) -> Dict[str, Any]:
        """
        Simplified tracking method with automatic parameter detection.
        
        This method provides the easiest way to track metrics by automatically
        detecting the billing model and using appropriate parameters.
        
        Args:
            **kwargs: Flexible parameters that will be mapped to appropriate tracking calls
                     Common parameters: value, workflow_type, activity_units, metadata
                     
        Returns:
            Dictionary containing recorded metrics.
            
        Example:
            >>> # Works for any billing model type
            >>> await client.simple_track(value=500.0, metadata={"source": "api"})
            >>> await client.simple_track(workflow_type="lead_research")
            >>> await client.simple_track(activity_units=3)
        """
        return await self.smart_track(
            value=kwargs.get('value'),
            metadata=kwargs.get('metadata'),
            activity_units=kwargs.get('activity_units', 1),
            outcome_type=kwargs.get('outcome_type'),
            workflow_type=kwargs.get('workflow_type')
        )

    # Utility and Helper Methods
    
    async def get_billing_model_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the agent's billing model including pricing.
        
        Returns:
            Dictionary with billing model details, supported types, and pricing information.
        """
        try:
            config = await self.get_billing_config()
            model_type = config.get("model_type")
            
            info = {
                "model_type": model_type,
                "model_name": config.get("model_name"),
                "is_active": config.get("is_active"),
                "supported_operations": [],
                "pricing_info": {}
            }
            
            if model_type == "agent":
                agent_config = config.get("agent_config", {})
                info["supported_operations"] = ["agent_usage"]
                info["pricing_info"] = {
                    "base_agent_fee": agent_config.get("base_agent_fee"),
                    "billing_frequency": agent_config.get("billing_frequency"),
                    "agent_tier": agent_config.get("agent_tier")
                }
                
            elif model_type == "activity":
                activity_configs = config.get("activity_configs", [])
                info["supported_operations"] = ["activities"]
                info["pricing_info"] = {
                    "activity_types": [
                        {
                            "type": cfg.get("activity_type"),
                            "price_per_unit": cfg.get("price_per_unit"),
                            "unit_type": cfg.get("unit_type")
                        }
                        for cfg in activity_configs if cfg.get("is_active")
                    ]
                }
                
            elif model_type == "outcome":
                outcome_configs = config.get("outcome_configs", [])
                info["supported_operations"] = ["outcomes"]
                info["pricing_info"] = {
                    "outcome_types": [
                        {
                            "type": cfg.get("outcome_type"),
                            "name": cfg.get("outcome_name"),
                            "percentage": cfg.get("percentage"),
                            "requires_verification": cfg.get("requires_verification")
                        }
                        for cfg in outcome_configs if cfg.get("is_active")
                    ]
                }
                
            elif model_type == "workflow":
                workflow_config = config.get("workflow_config", {})
                workflow_types = config.get("workflow_types", [])
                info["supported_operations"] = ["workflows"]
                info["pricing_info"] = {
                    "base_platform_fee": workflow_config.get("base_platform_fee"),
                    "platform_fee_frequency": workflow_config.get("platform_fee_frequency"),
                    "currency": workflow_config.get("currency"),
                    "workflow_types": [
                        {
                            "type": wt.get("workflow_type"),
                            "name": wt.get("workflow_name"),
                            "price_per_workflow": wt.get("price_per_workflow"),
                            "complexity_level": wt.get("complexity_level")
                        }
                        for wt in workflow_types if wt.get("is_active")
                    ]
                }
            
            return info
            
        except Exception as e:
            return {"error": f"Failed to get billing model info: {str(e)}"}
    
    async def estimate_cost(self, **kwargs) -> Dict[str, Any]:
        """
        Estimate cost for operations without actually recording them.
        
        Args:
            **kwargs: Parameters for cost estimation
                     - activity_units: Number of activity units
                     - outcome_value: Value for outcome calculation
                     - workflow_executions: Dict of workflow types to counts
                     
        Returns:
            Dictionary with cost estimates.
        """
        try:
            config = await self.get_billing_config()
            model_type = config.get("model_type")
            
            estimate = {
                "model_type": model_type,
                "estimated_cost": 0.0,
                "currency": "USD",
                "breakdown": {}
            }
            
            if model_type == "activity":
                activity_units = kwargs.get("activity_units", 1)
                activity_configs = config.get("activity_configs", [])
                total_cost = 0.0
                
                for cfg in activity_configs:
                    if cfg.get("is_active"):
                        unit_cost = cfg.get("price_per_unit", 0) * activity_units
                        total_cost += unit_cost
                        estimate["breakdown"][cfg.get("activity_type")] = unit_cost
                
                estimate["estimated_cost"] = total_cost
                
            elif model_type == "outcome":
                outcome_value = kwargs.get("outcome_value", 0)
                outcome_configs = config.get("outcome_configs", [])
                total_cost = 0.0
                
                for cfg in outcome_configs:
                    if cfg.get("is_active"):
                        percentage_cost = outcome_value * (cfg.get("percentage", 0) / 100.0)
                        total_cost += percentage_cost
                        estimate["breakdown"][cfg.get("outcome_type")] = percentage_cost
                
                estimate["estimated_cost"] = total_cost
                
            elif model_type == "workflow":
                workflow_executions = kwargs.get("workflow_executions", {})
                if workflow_executions:
                    validation = await self.validate_workflow_data(workflow_executions)
                    estimate["estimated_cost"] = validation.get("total_estimated_cost", 0.0)
                    estimate["breakdown"] = validation.get("workflow_validations", {})
                    estimate["currency"] = config.get("workflow_config", {}).get("currency", "USD")
            
            return estimate
            
        except Exception as e:
            return {"error": f"Cost estimation failed: {str(e)}"}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the agent and its billing configuration.
        
        Returns:
            Dictionary with health status and any configuration issues.
        """
        health = {
            "agent_exists": False,
            "billing_model_configured": False,
            "billing_model_active": False,
            "supported_operations": [],
            "warnings": [],
            "status": "unknown"
        }
        
        try:
            # Check if agent exists
            agent_info = await self.get_agent_info()
            health["agent_exists"] = True
            health["agent_name"] = agent_info.get("name")
            health["agent_active"] = agent_info.get("is_active")
            
            # Check billing configuration
            try:
                config = await self.get_billing_config()
                health["billing_model_configured"] = True
                health["billing_model_active"] = config.get("is_active", False)
                health["model_type"] = config.get("model_type")
                
                # Determine supported operations
                model_type = config.get("model_type")
                if model_type == "activity":
                    health["supported_operations"] = await self.get_supported_activities()
                elif model_type == "outcome":
                    health["supported_operations"] = await self.get_supported_outcomes()
                elif model_type == "workflow":
                    workflows = await self.get_supported_workflows()
                    health["supported_operations"] = [w["type"] for w in workflows]
                elif model_type == "agent":
                    health["supported_operations"] = ["agent_usage"]
                
                # Check for potential issues
                if not health["supported_operations"]:
                    health["warnings"].append("No active configurations found for billing model")
                
                if not health["billing_model_active"]:
                    health["warnings"].append("Billing model is configured but not active")
                    
            except Exception as e:
                health["warnings"].append(f"Billing configuration error: {str(e)}")
            
            # Determine overall status
            if health["agent_exists"] and health["billing_model_configured"] and health["billing_model_active"]:
                health["status"] = "healthy"
            elif health["agent_exists"] and health["billing_model_configured"]:
                health["status"] = "warning"
            else:
                health["status"] = "error"
                
        except Exception as e:
            health["warnings"].append(f"Health check error: {str(e)}")
            health["status"] = "error"
        
        return health
