import pytest

ORG_DATA = {"name": "Org1", "description": "Test organization"}


def test_read_organizations_empty(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/organizations/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_organization(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/organizations/",
        json=ORG_DATA,
        headers=headers
    )
    assert response.status_code == 200
    org = response.json()
    assert org["name"] == ORG_DATA["name"]
    pytest.global_org_id = org["id"]


def test_get_organization(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = pytest.global_org_id
    response = client.get(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 200
    org = response.json()
    assert org["id"] == org_id


def test_update_organization(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = pytest.global_org_id
    new_desc = "Updated organization"
    response = client.put(
        f"/api/v1/organizations/{org_id}",
        json={"description": new_desc},
        headers=headers
    )
    assert response.status_code == 200
    org = response.json()
    assert org["description"] == new_desc


def test_delete_organization(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = pytest.global_org_id
    response = client.delete(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 200
    # subsequent get should 404
    response = client.get(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 404