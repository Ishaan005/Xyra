import pytest
from datetime import datetime

BM_DATA = {
    "name": "BM1",
    "description": "Test billing model",
    "model_type": "agent",
    "agent_price_per_agent": 10.0,
    "agent_billing_frequency": "monthly",
    "agent_base_agent_fee": 5.0,  # Added required field
}
UPDATED_NAME = "BM1 Updated"

# Global variable to store billing model ID across tests
bm_id = None


@pytest.fixture()
def setup_org(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    body = {"name": "OrgBM", "description": ""}
    res = client.post(
        "/api/v1/organizations/", json=body, headers=headers
    )
    if res.status_code == 200:
        data = res.json()
        return data["id"]
    # If already exists, fetch from list
    list_res = client.get("/api/v1/organizations/", headers=headers)
    assert list_res.status_code == 200, f"Failed to list organizations: {list_res.status_code}, {list_res.text}"
    for org in list_res.json():
        if org.get("name") == body["name"]:
            return org["id"]
    pytest.skip("OrgBM not found and could not be created")


def test_read_billing_models_empty(client, token, setup_org):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = setup_org
    response = client.get(f"/api/v1/billing-models/?org_id={org_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_billing_model(client, token, setup_org):
    global bm_id
    headers = {"Authorization": f"Bearer {token}"}
    data = {**BM_DATA, "organization_id": setup_org}
    response = client.post(
        "/api/v1/billing-models/",
        json=data,
        headers=headers
    )
    assert response.status_code == 200
    bm = response.json()
    assert bm["name"] == BM_DATA["name"]
    bm_id = bm["id"]


def test_read_billing_model(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/billing-models/{bm_id}", headers=headers)
    assert response.status_code == 200
    bm = response.json()
    assert bm["id"] == bm_id


def test_update_billing_model(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/api/v1/billing-models/{bm_id}",
        json={"name": UPDATED_NAME},
        headers=headers
    )
    assert response.status_code == 200
    bm = response.json()
    assert bm["name"] == UPDATED_NAME


def test_calculate_billing_cost(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    usage_data = {"agents": 5}  # Changed from "seats" to "agents"
    response = client.post(
        f"/api/v1/billing-models/{bm_id}/calculate",
        json=usage_data,
        headers=headers
    )
    assert response.status_code == 200
    cost_data = response.json()
    assert cost_data["billing_model_id"] == bm_id
    assert cost_data["currency"] == "USD"
    assert isinstance(cost_data["cost"], float)


def test_create_and_calculate_outcome_billing_model(client, token, setup_org):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test case 1: Both percentage and fixed charge
    outcome_data_1 = {
        "name": "Outcome BM 1",
        "description": "Test outcome billing model with both charges",
        "model_type": "outcome",
        "organization_id": setup_org,
        "outcome_outcome_name": "Test Outcome",
        "outcome_outcome_type": "revenue_uplift",
        "outcome_percentage": 10.0,
        "outcome_fixed_charge_per_outcome": 5.0,
        "outcome_risk_premium_percentage": 0.0  # Disable risk premium for test
    }
    
    response = client.post("/api/v1/billing-models/", json=outcome_data_1, headers=headers)
    assert response.status_code == 200
    bm1 = response.json()
    bm1_id = bm1["id"]

    usage_data_1 = {"outcome_value": 1000, "outcome_count": 10}
    response = client.post(f"/api/v1/billing-models/{bm1_id}/calculate", json=usage_data_1, headers=headers)
    assert response.status_code == 200
    cost_data_1 = response.json()
    # cost = (1000 * 0.10) + (10 * 5.0) = 100 + 50 = 150
    assert cost_data_1["cost"] == 150.0

    # Test case 2: Only percentage
    outcome_data_2 = {
        "name": "Outcome BM 2",
        "description": "Test outcome billing model with percentage only",
        "model_type": "outcome",
        "organization_id": setup_org,
        "outcome_outcome_name": "Test Outcome 2",
        "outcome_outcome_type": "revenue_uplift",
        "outcome_percentage": 15.0,
        "outcome_risk_premium_percentage": 0.0  # Disable risk premium for test
    }

    response = client.post("/api/v1/billing-models/", json=outcome_data_2, headers=headers)
    assert response.status_code == 200
    bm2 = response.json()
    bm2_id = bm2["id"]

    usage_data_2 = {"outcome_value": 1000, "outcome_count": 10}
    response = client.post(f"/api/v1/billing-models/{bm2_id}/calculate", json=usage_data_2, headers=headers)
    assert response.status_code == 200
    cost_data_2 = response.json()
    # cost = 1000 * 0.15 = 150
    assert cost_data_2["cost"] == 150.0

    # Test case 3: Only fixed charge
    outcome_data_3 = {
        "name": "Outcome BM 3",
        "description": "Test outcome billing model with fixed charge only",
        "model_type": "outcome",
        "organization_id": setup_org,
        "outcome_outcome_name": "Test Outcome 3",
        "outcome_outcome_type": "lead_generation",
        "outcome_fixed_charge_per_outcome": 7.5,
        "outcome_risk_premium_percentage": 0.0  # Disable risk premium for test
    }

    response = client.post("/api/v1/billing-models/", json=outcome_data_3, headers=headers)
    assert response.status_code == 200
    bm3 = response.json()
    bm3_id = bm3["id"]

    usage_data_3 = {"outcome_value": 1000, "outcome_count": 20}
    response = client.post(f"/api/v1/billing-models/{bm3_id}/calculate", json=usage_data_3, headers=headers)
    assert response.status_code == 200
    cost_data_3 = response.json()
    # cost = 20 * 7.5 = 150
    assert cost_data_3["cost"] == 150.0
    
    # Test case 4: Validation failure - neither is provided
    outcome_data_4 = {
        "name": "Outcome BM 4",
        "description": "Test outcome billing model with no charges",
        "model_type": "outcome",
        "organization_id": setup_org,
        "outcome_outcome_name": "Test Outcome 4",
        "outcome_outcome_type": "revenue_uplift"
    }
    response = client.post("/api/v1/billing-models/", json=outcome_data_4, headers=headers)
    assert response.status_code == 400  # Bad Request for business logic validation

    # Cleanup created models
    client.delete(f"/api/v1/billing-models/{bm1_id}", headers=headers)
    client.delete(f"/api/v1/billing-models/{bm2_id}", headers=headers)
    client.delete(f"/api/v1/billing-models/{bm3_id}", headers=headers)


def test_delete_billing_model(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/api/v1/billing-models/{bm_id}", headers=headers)
    assert response.status_code == 200
    response = client.get(f"/api/v1/billing-models/{bm_id}", headers=headers)
    assert response.status_code == 404
