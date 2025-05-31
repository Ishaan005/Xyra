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
