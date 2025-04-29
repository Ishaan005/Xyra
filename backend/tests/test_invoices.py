import pytest
from datetime import datetime, timedelta

@pytest.fixture()
def setup_org(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    body = {"name": "OrgInv", "description": ""}
    res = client.post(
        "/api/v1/organizations/", json=body, headers=headers
    )
    if res.status_code == 200:
        return res.json()["id"]
    # If already exists, fetch existing
    list_res = client.get("/api/v1/organizations/", headers=headers)
    assert list_res.status_code == 200, f"Failed to list organizations: {list_res.status_code}, {list_res.text}"
    for org in list_res.json():
        if org.get("name") == body["name"]:
            return org["id"]
    pytest.skip("OrgInv not found and could not be created")


@pytest.fixture()
def invoice_items():
    # Single line item
    return [{
        "description": "Test item",
        "quantity": 2.0,
        "unit_price": 15.0,
        "amount": 30.0,
        "item_type": "subscription"
    }]


def test_read_invoices_empty(client, token, setup_org):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = setup_org
    response = client.get(f"/api/v1/invoices/?org_id={org_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_invoice(client, token, setup_org, invoice_items):
    headers = {"Authorization": f"Bearer {token}"}
    due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    data = {
        "organization_id": setup_org,
        "due_date": due_date,
        "items": invoice_items
    }
    response = client.post(
        "/api/v1/invoices/",
        json=data,
        headers=headers
    )
    assert response.status_code == 200
    inv = response.json()
    assert inv["organization_id"] == setup_org
    global invoice_id
    invoice_id = inv["id"]


def test_read_invoice(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/invoices/{invoice_id}", headers=headers)
    assert response.status_code == 200
    inv = response.json()
    assert inv["id"] == invoice_id


def test_update_invoice(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/api/v1/invoices/{invoice_id}",
        json={"notes": "Updated note"},
        headers=headers
    )
    assert response.status_code == 200
    inv = response.json()
    assert inv.get("notes") == "Updated note"


def test_cancel_invoice(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/api/v1/invoices/{invoice_id}/cancel", headers=headers)
    assert response.status_code == 200
    inv = response.json()
    assert inv["status"] == "cancelled"


def test_pay_invoice(client, token, setup_org, invoice_items):
    # Create new invoice for payment
    headers = {"Authorization": f"Bearer {token}"}
    due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    data = {"organization_id": setup_org, "due_date": due_date, "items": invoice_items}
    res = client.post("/api/v1/invoices/", json=data, headers=headers)
    new_inv = res.json()
    inv_id = new_inv["id"]

    payment_data = {"payment_method": "card", "payment_date": datetime.utcnow().isoformat()}
    response = client.post(
        f"/api/v1/invoices/{inv_id}/pay",
        json=payment_data,
        headers=headers
    )
    assert response.status_code == 200
    paid = response.json()
    assert paid["status"] == "paid"


def test_generate_monthly_invoice_invalid_month(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/invoices/generate/monthly?org_id=1&year=2025&month=13",
        headers=headers
    )
    assert response.status_code == 400


def test_generate_monthly_invoice(client, token, setup_org):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        f"/api/v1/invoices/generate/monthly?org_id={setup_org}&year=2025&month=1",
        headers=headers
    )
    # No agents or billable items, expect 400 error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    # Error can be due to no agents or no billable items
    assert any(
        msg in data["detail"] for msg in ["No agents found", "No billable items"]
    ), f"Unexpected error detail: {data['detail']}"
