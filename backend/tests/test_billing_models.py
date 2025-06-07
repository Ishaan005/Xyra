import pytest
from datetime import datetime

BM_DATA = {
    "name": "BM1",
    "description": "Test billing model",
    "model_type": "seat",
    "seat_price_per_seat": 10.0,
    "seat_billing_frequency": "monthly",
}
UPDATED_NAME = "BM1 Updated"


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
    global bm_id
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
    usage_data = {"seats": 5}
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


def test_delete_billing_model(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/api/v1/billing-models/{bm_id}", headers=headers)
    assert response.status_code == 200
    response = client.get(f"/api/v1/billing-models/{bm_id}", headers=headers)
    assert response.status_code == 404
