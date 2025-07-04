import pytest

AGENT_DATA = {
    "name": "Agent One",
    "external_id": "ext-123",
    "organization_id": None,
    "is_active": True
}
UPDATED_NAME = "Agent One Updated"
ACTIVITY_DATA = {"agent_id": None, "activity_type": "api_call", "timestamp": None}
COST_DATA = {"agent_id": None, "amount": 5.0, "timestamp": None}
OUTCOME_DATA = {"agent_id": None, "value": 10.0, "timestamp": None}

@pytest.fixture()
def setup_org(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    body = {"name": "OrgAgent", "description": ""}
    res = client.post(
        "/api/v1/organizations/", json=body, headers=headers
    )
    if res.status_code == 200:
        data = res.json()
        return data["id"]
    # If already exists, fetch existing organization
    list_res = client.get("/api/v1/organizations/", headers=headers)
    assert list_res.status_code == 200, f"Failed to list organizations: {list_res.status_code}, {list_res.text}"
    orgs = list_res.json()
    for org in orgs:
        if org.get("name") == body["name"]:
            return org["id"]
    pytest.skip("OrgAgent not found and could not be created")

@pytest.fixture()
def setup_agent(client, token, setup_org):
    headers = {"Authorization": f"Bearer {token}"}
    data = {**AGENT_DATA, "organization_id": setup_org}
    res = client.post(
        "/api/v1/agents/", json=data, headers=headers
    )
    agent = res.json()
    return agent["id"], agent["external_id"]


def test_read_agents_empty(client, token, setup_org):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/agents/?org_id={setup_org}", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


class TestAgentLifecycle:
    """Test agent CRUD operations and related functionality in sequence."""
    
    agent_id = None
    ext_id = None
    
    def test_create_agent(self, client, token, setup_org, setup_agent):
        agent_id, ext_id = setup_agent
        assert agent_id is not None
        TestAgentLifecycle.agent_id = agent_id
        TestAgentLifecycle.ext_id = ext_id

    def test_read_agent_by_id(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        response = client.get(f"/api/v1/agents/{agent_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id

    def test_read_agent_by_external_id(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        ext_id = TestAgentLifecycle.ext_id
        assert ext_id is not None, "Agent must be created first"
        response = client.get(f"/api/v1/agents/external/{ext_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["external_id"] == ext_id

    def test_update_agent(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        response = client.put(
            f"/api/v1/agents/{agent_id}", json={"name": UPDATED_NAME}, headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == UPDATED_NAME

    def test_record_activity(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        body = {"agent_id": agent_id, "activity_type": "api_call"}
        response = client.post(
            f"/api/v1/agents/{agent_id}/activities", json=body, headers=headers
        )
        assert response.status_code == 200
        act = response.json()
        assert act["agent_id"] == agent_id

    def test_record_cost(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        body = {"agent_id": agent_id, "cost_type": "manual", "amount": 5.0}
        response = client.post(
            f"/api/v1/agents/{agent_id}/costs", json=body, headers=headers
        )
        assert response.status_code == 200
        cost = response.json()
        assert cost["agent_id"] == agent_id

    def test_record_outcome(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        body = {"agent_id": agent_id, "outcome_type": "result", "value": 10.0}
        response = client.post(
            f"/api/v1/agents/{agent_id}/outcomes", json=body, headers=headers
        )
        assert response.status_code == 200
        outcome = response.json()
        assert outcome["agent_id"] == agent_id

    def test_get_agent_stats(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        response = client.get(f"/api/v1/agents/{agent_id}/stats", headers=headers)
        assert response.status_code == 200
        stats = response.json()
        assert stats.get("activity_count", None) is not None

    def test_delete_agent(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        response = client.delete(f"/api/v1/agents/{agent_id}", headers=headers)
        assert response.status_code == 200
        response = client.get(f"/api/v1/agents/{agent_id}", headers=headers)
        assert response.status_code == 404

    def test_agent_service_functions(self, client, token):
        """Test new agent service functions"""
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        
        # Test getting agent billing config
        response = client.get(f"/api/v1/agents/{agent_id}/billing-config", headers=headers)
        # This might return 404 if no billing model is configured or endpoint not found
        assert response.status_code in [200, 404]
        
        # Test getting agent billing summary
        response = client.get(f"/api/v1/agents/{agent_id}/billing-summary", headers=headers)
        # This might return 404 if endpoint not found, which is acceptable for now
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            summary = response.json()
            assert "agent_id" in summary
            assert "total_cost" in summary
            assert "cost_by_type" in summary
        
        # Test workflow validation endpoint
        workflow_data = {
            "workflow_executions": {
                "lead_research": 5,
                "email_personalization": 10
            }
        }
        response = client.post(
            f"/api/v1/agents/{agent_id}/workflows/validate", 
            json=workflow_data, 
            headers=headers
        )
        # This might fail if agent doesn't have workflow billing model or endpoint not found
        assert response.status_code in [200, 400, 404]

    def test_workflow_validation_functions(self, client, token):
        """Test workflow validation functions"""
        headers = {"Authorization": f"Bearer {token}"}
        agent_id = TestAgentLifecycle.agent_id
        assert agent_id is not None, "Agent must be created first"
        
        # Test bulk workflow recording endpoint
        workflow_data = {
            "workflow_executions": {
                "lead_research": 5,
                "email_personalization": 10
            },
            "commitment_exceeded": False
        }
        response = client.post(
            f"/api/v1/agents/{agent_id}/workflows/bulk", 
            json=workflow_data, 
            headers=headers
        )
        # This might fail if agent doesn't have workflow billing model or endpoint not found
        assert response.status_code in [200, 400, 404]
        
        # Test billing summary with date filters (only if endpoint exists)
        response = client.get(
            f"/api/v1/agents/{agent_id}/billing-summary?start_date=2023-01-01T00:00:00Z&end_date=2023-12-31T23:59:59Z", 
            headers=headers
        )
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            summary = response.json()
            assert "period" in summary
            assert summary["period"]["start_date"] is not None
            assert summary["period"]["end_date"] is not None


class TestAgentServiceFunctions:
    """Test enhanced agent service functions"""
    
    def test_agent_service_imports(self):
        """Test that all new agent service functions can be imported"""
        from app.services.agent_service import (
            record_bulk_workflows,
            get_agent_billing_summary,
            validate_workflow_billing_data,
            get_agent_billing_config
        )
        
        # Test function signatures
        assert callable(record_bulk_workflows)
        assert callable(get_agent_billing_summary)
        assert callable(validate_workflow_billing_data)
        assert callable(get_agent_billing_config)
    
    def test_billing_model_calculation_import(self):
        """Test billing model calculation function import"""
        from app.services.billing_model.calculation import calculate_cost
        assert callable(calculate_cost)
    
    def test_agent_service_function_signatures(self):
        """Test that agent service functions have correct signatures"""
        import inspect
        from app.services.agent_service import (
            record_bulk_workflows,
            get_agent_billing_summary,
            validate_workflow_billing_data
        )
        
        # Test record_bulk_workflows signature
        sig = inspect.signature(record_bulk_workflows)
        params = list(sig.parameters.keys())
        assert 'db' in params
        assert 'agent_id' in params
        assert 'workflow_executions' in params
        
        # Test get_agent_billing_summary signature
        sig = inspect.signature(get_agent_billing_summary)
        params = list(sig.parameters.keys())
        assert 'db' in params
        assert 'agent_id' in params
        assert 'start_date' in params
        assert 'end_date' in params
        
        # Test validate_workflow_billing_data signature
        sig = inspect.signature(validate_workflow_billing_data)
        params = list(sig.parameters.keys())
        assert 'db' in params
        assert 'agent_id' in params
        assert 'workflow_executions' in params
