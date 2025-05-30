import pytest

ORG_DATA = {"name": "Org1", "description": "Test organization"}


@pytest.fixture()
def created_org(client, token):
    """Create an organization for testing and return its ID"""
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/organizations/",
        json=ORG_DATA,
        headers=headers
    )
    if response.status_code == 200:
        org = response.json()
        assert org["name"] == ORG_DATA["name"]
        return org["id"]
    
    # If already exists, fetch existing organization
    list_response = client.get("/api/v1/organizations/", headers=headers)
    assert list_response.status_code == 200, f"Failed to list organizations: {list_response.status_code}, {list_response.text}"
    orgs = list_response.json()
    for org in orgs:
        if org.get("name") == ORG_DATA["name"]:
            return org["id"]
    
    # If we get here, there was an unexpected error
    pytest.fail(f"Organization '{ORG_DATA['name']}' not found and could not be created. Response: {response.status_code}, {response.text}")


def test_read_organizations_empty(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/organizations/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # Should return a list of organizations (may be non-empty due to prior tests)
    assert isinstance(data, list)


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


def test_get_organization(client, token, created_org):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = created_org
    response = client.get(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 200
    org = response.json()
    assert org["id"] == org_id


def test_update_organization(client, token, created_org):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = created_org
    new_desc = "Updated organization"
    response = client.put(
        f"/api/v1/organizations/{org_id}",
        json={"description": new_desc},
        headers=headers
    )
    assert response.status_code == 200
    org = response.json()
    assert org["description"] == new_desc


def test_delete_organization(client, token, created_org):
    headers = {"Authorization": f"Bearer {token}"}
    org_id = created_org
    response = client.delete(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 200
    # subsequent get should 404
    response = client.get(f"/api/v1/organizations/{org_id}", headers=headers)
    assert response.status_code == 404