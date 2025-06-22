import pytest
from datetime import datetime

# Test data for workflow-based billing models
WORKFLOW_BM_DATA = {
    "name": "SDR Agent Workflow Billing",
    "description": "Workflow-based pricing for Sales Development Representative agent",
    "model_type": "workflow",
    "workflow_base_platform_fee": 3000.0,  # $3,000/month base platform fee
    "workflow_platform_fee_frequency": "monthly",
    "workflow_default_billing_frequency": "monthly",
    "workflow_volume_discount_enabled": True,
    "workflow_volume_discount_threshold": 50,  # 20% off after 50 workflows/month
    "workflow_volume_discount_percentage": 20.0,
    "workflow_overage_multiplier": 1.0,
    "workflow_currency": "USD",
    "workflow_is_active": True,
    "workflow_types": [
        {
            "workflow_name": "Lead Research",
            "workflow_type": "lead_research",
            "description": "Comprehensive lead profiling and research",
            "price_per_workflow": 2.0,
            "estimated_compute_cost": 0.50,
            "estimated_duration_minutes": 5,
            "complexity_level": "simple",
            "expected_roi_multiplier": 10.0,
            "business_value_category": "lead_generation",
            "volume_tier_1_threshold": 100,
            "volume_tier_1_price": 1.80,
            "volume_tier_2_threshold": 500,
            "volume_tier_2_price": 1.50,
            "volume_tier_3_threshold": 1000,
            "volume_tier_3_price": 1.20,
            "billing_frequency": "monthly",
            "minimum_charge": 0.0,
            "is_active": True
        },
        {
            "workflow_name": "Email Personalization", 
            "workflow_type": "email_personalization",
            "description": "AI-crafted personalized email outreach",
            "price_per_workflow": 1.0,
            "estimated_compute_cost": 0.25,
            "estimated_duration_minutes": 2,
            "complexity_level": "simple",
            "expected_roi_multiplier": 8.0,
            "business_value_category": "lead_generation",
            "volume_tier_1_threshold": 200,
            "volume_tier_1_price": 0.90,
            "volume_tier_2_threshold": 1000,
            "volume_tier_2_price": 0.75,
            "billing_frequency": "monthly",
            "minimum_charge": 0.0,
            "is_active": True
        },
        {
            "workflow_name": "LinkedIn Outreach",
            "workflow_type": "linkedin_outreach", 
            "description": "Automated LinkedIn connection requests with personalization",
            "price_per_workflow": 3.0,
            "estimated_compute_cost": 0.75,
            "estimated_duration_minutes": 8,
            "complexity_level": "medium",
            "expected_roi_multiplier": 12.0,
            "business_value_category": "lead_generation",
            "volume_tier_1_threshold": 50,
            "volume_tier_1_price": 2.70,
            "volume_tier_2_threshold": 200,
            "volume_tier_2_price": 2.40,
            "billing_frequency": "monthly",
            "minimum_charge": 0.0,
            "is_active": True
        },
        {
            "workflow_name": "Meeting Booking",
            "workflow_type": "meeting_booking",
            "description": "End-to-end meeting scheduling and coordination",
            "price_per_workflow": 8.0,
            "estimated_compute_cost": 2.0,
            "estimated_duration_minutes": 15,
            "complexity_level": "complex",
            "expected_roi_multiplier": 25.0,
            "business_value_category": "revenue_growth",
            "volume_tier_1_threshold": 25,
            "volume_tier_1_price": 7.20,
            "volume_tier_2_threshold": 100,
            "volume_tier_2_price": 6.40,
            "billing_frequency": "monthly",
            "minimum_charge": 8.0,
            "is_active": True
        }
    ],
    "commitment_tiers": [
        {
            "tier_name": "Starter",
            "tier_level": 1,
            "description": "Perfect for small teams getting started",
            "minimum_workflows_per_month": 500,
            "minimum_monthly_revenue": 5000.0,
            "included_workflows": 0,
            "included_workflow_types": None,
            "discount_percentage": 0.0,
            "platform_fee_discount": 0.0,
            "commitment_period_months": 12,
            "overage_rate_multiplier": 1.0,
            "is_active": True,
            "is_popular": False
        },
        {
            "tier_name": "Growth", 
            "tier_level": 2,
            "description": "Best value for growing sales teams",
            "minimum_workflows_per_month": 2000,
            "minimum_monthly_revenue": 12500.0,
            "included_workflows": 100,
            "included_workflow_types": '["lead_research", "email_personalization"]',
            "discount_percentage": 10.0,
            "platform_fee_discount": 500.0,
            "commitment_period_months": 12,
            "overage_rate_multiplier": 1.0,
            "is_active": True,
            "is_popular": True
        },
        {
            "tier_name": "Scale",
            "tier_level": 3,
            "description": "Enterprise-grade solution for large teams",
            "minimum_workflows_per_month": 10000,
            "minimum_monthly_revenue": 25000.0,
            "included_workflows": 1000,
            "included_workflow_types": '["lead_research", "email_personalization", "linkedin_outreach"]',
            "discount_percentage": 20.0,
            "platform_fee_discount": 1500.0,
            "commitment_period_months": 24,
            "overage_rate_multiplier": 0.9,
            "is_active": True,
            "is_popular": False
        }
    ]
}

FINANCIAL_WORKFLOW_BM_DATA = {
    "name": "CFO Assistant Workflow Billing",
    "description": "Workflow-based pricing for Financial Analysis agent",
    "model_type": "workflow",
    "workflow_base_platform_fee": 5000.0,  # $5,000/month base platform fee
    "workflow_platform_fee_frequency": "monthly",
    "workflow_default_billing_frequency": "monthly",
    "workflow_volume_discount_enabled": True,
    "workflow_volume_discount_threshold": 50,
    "workflow_volume_discount_percentage": 20.0,
    "workflow_overage_multiplier": 1.0,
    "workflow_currency": "USD",
    "workflow_is_active": True,
    "workflow_types": [
        {
            "workflow_name": "Report Creation",
            "workflow_type": "report_creation",
            "description": "Automated financial report generation",
            "price_per_workflow": 100.0,
            "estimated_compute_cost": 25.0,
            "estimated_duration_minutes": 30,
            "complexity_level": "medium",
            "expected_roi_multiplier": 5.0,
            "business_value_category": "cost_savings",
            "volume_tier_1_threshold": 20,
            "volume_tier_1_price": 80.0,
            "billing_frequency": "monthly",
            "minimum_charge": 100.0,
            "is_active": True
        },
        {
            "workflow_name": "Cash Flow Forecast",
            "workflow_type": "cash_flow_forecast",
            "description": "AI-powered cash flow forecasting and analysis",
            "price_per_workflow": 250.0,
            "estimated_compute_cost": 50.0,
            "estimated_duration_minutes": 45,
            "complexity_level": "complex",
            "expected_roi_multiplier": 15.0,
            "business_value_category": "revenue_growth",
            "billing_frequency": "monthly",
            "minimum_charge": 250.0,
            "is_active": True
        },
        {
            "workflow_name": "Budget vs Actual Report",
            "workflow_type": "budget_vs_actual",
            "description": "Department-wise budget variance analysis",
            "price_per_workflow": 50.0,
            "estimated_compute_cost": 15.0,
            "estimated_duration_minutes": 20,
            "complexity_level": "medium",
            "expected_roi_multiplier": 8.0,
            "business_value_category": "cost_savings",
            "billing_frequency": "monthly",
            "minimum_charge": 50.0,
            "is_active": True
        },
        {
            "workflow_name": "Board Deck Generation",
            "workflow_type": "board_deck_generation",
            "description": "Executive-ready board presentation creation",
            "price_per_workflow": 500.0,
            "estimated_compute_cost": 100.0,
            "estimated_duration_minutes": 90,
            "complexity_level": "complex",
            "expected_roi_multiplier": 20.0,
            "business_value_category": "revenue_growth",
            "billing_frequency": "monthly",
            "minimum_charge": 500.0,
            "is_active": True
        },
        {
            "workflow_name": "Real-time Dashboard Update",
            "workflow_type": "dashboard_update",
            "description": "Live financial dashboard data refresh",
            "price_per_workflow": 25.0,
            "estimated_compute_cost": 5.0,
            "estimated_duration_minutes": 5,
            "complexity_level": "simple",
            "expected_roi_multiplier": 3.0,
            "business_value_category": "cost_savings",
            "billing_frequency": "per_use",
            "minimum_charge": 25.0,
            "is_active": True
        }
    ]
}

UPDATED_NAME = "Updated Workflow Model"


@pytest.fixture()
def setup_org(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    body = {"name": "OrgWorkflow", "description": ""}
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
    pytest.skip("OrgWorkflow not found and could not be created")


@pytest.fixture()
def workflow_billing_model(client, token, setup_org):
    """Create a workflow billing model for testing"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {**WORKFLOW_BM_DATA, "organization_id": setup_org}
    response = client.post(
        "/api/v1/billing-models/",
        json=data,
        headers=headers
    )
    assert response.status_code == 200
    bm = response.json()
    assert bm["name"] == WORKFLOW_BM_DATA["name"]
    assert bm["model_type"] == "workflow"
    return bm["id"]


def test_create_workflow_billing_model_sdr(client, token, setup_org):
    """Test creating a comprehensive SDR workflow-based billing model"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {**WORKFLOW_BM_DATA, "organization_id": setup_org}
    response = client.post(
        "/api/v1/billing-models/",
        json=data,
        headers=headers
    )
    assert response.status_code == 200
    bm = response.json()
    assert bm["name"] == WORKFLOW_BM_DATA["name"]
    assert bm["model_type"] == "workflow"


def test_create_workflow_billing_model_financial(client, token, setup_org):
    """Test creating a financial analysis workflow-based billing model"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {**FINANCIAL_WORKFLOW_BM_DATA, "organization_id": setup_org}
    response = client.post(
        "/api/v1/billing-models/",
        json=data,
        headers=headers
    )
    assert response.status_code == 200
    bm = response.json()
    assert bm["name"] == FINANCIAL_WORKFLOW_BM_DATA["name"]
    assert bm["model_type"] == "workflow"


def test_read_workflow_billing_model(client, token, workflow_billing_model):
    """Test reading a workflow-based billing model with all relationships"""
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/billing-models/{workflow_billing_model}", headers=headers)
    assert response.status_code == 200
    bm = response.json()
    assert bm["id"] == workflow_billing_model
    assert bm["model_type"] == "workflow"
    
    # Check that workflow config exists
    assert "workflow_config" in bm
    # Check that workflow types exist
    assert "workflow_types" in bm and len(bm["workflow_types"]) > 0
    # Check that commitment tiers exist
    assert "commitment_tiers" in bm and len(bm["commitment_tiers"]) > 0


def test_calculate_workflow_cost_simple(client, token, workflow_billing_model):
    """Test basic workflow cost calculation"""
    headers = {"Authorization": f"Bearer {token}"}
    usage_data = {
        "workflows": {
            "lead_research": 10,
            "email_personalization": 20,
            "linkedin_outreach": 5,
            "meeting_booking": 2
        }
    }
    response = client.post(
        f"/api/v1/billing-models/{workflow_billing_model}/calculate",
        json=usage_data,
        headers=headers
    )
    if response.status_code != 200:
        print(f"Error response: {response.status_code}, {response.text}")
    assert response.status_code == 200
    cost_data = response.json()
    assert cost_data["billing_model_id"] == workflow_billing_model
    assert cost_data["currency"] == "USD"
    assert isinstance(cost_data["cost"], float)
     # Expected cost (using volume tier 1 pricing as configured):
    # Base platform fee: $3,000
    # Lead research: 10 * $1.80 = $18 (volume tier 1 price)
    # Email personalization: 20 * $0.90 = $18 (volume tier 1 price)
    # LinkedIn outreach: 5 * $2.70 = $13.50 (volume tier 1 price)
    # Meeting booking: 2 * $7.20 = $14.40 (volume tier 1 price)
    # Total: $3,063.90
    expected_cost = 3000.0 + (10 * 1.80) + (20 * 0.90) + (5 * 2.70) + (2 * 7.20)
    print(f"Expected cost: {expected_cost}, Actual cost: {cost_data['cost']}")
    # Allow for small floating point differences
    assert abs(cost_data["cost"] - expected_cost) < 1.0


def test_calculate_workflow_cost_with_volume_pricing(client, token, workflow_billing_model):
    """Test workflow cost calculation with volume pricing tiers"""
    headers = {"Authorization": f"Bearer {token}"}
    usage_data = {
        "workflows": {
            "lead_research": 150,  # Crosses volume tier threshold
            "email_personalization": 250,  # Crosses volume tier threshold
        }
    }
    response = client.post(
        f"/api/v1/billing-models/{workflow_billing_model}/calculate",
        json=usage_data,
        headers=headers
    )
    assert response.status_code == 200
    cost_data = response.json()
    
    # Expected cost for lead_research (150 workflows):
    # First 100 at $1.80 = $180
    # Next 50 at $1.50 = $75
    # Total lead_research = $255
    
    # Expected cost for email_personalization (250 workflows):
    # First 200 at $0.90 = $180
    # Next 50 at $0.75 = $37.50
    # Total email_personalization = $217.50
    
    # Base platform fee: $3,000
    # Total: $3,000 + $255 + $217.50 = $3,472.50
    # But with 400 total workflows (>50), 20% global discount applies
    # Final: $3,472.50 * 0.8 = $2,778.00
    expected_lead_cost = (100 * 1.80) + (50 * 1.50)
    expected_email_cost = (200 * 0.90) + (50 * 0.75)
    expected_subtotal = 3000.0 + expected_lead_cost + expected_email_cost
    expected_total = expected_subtotal * 0.8  # 20% global volume discount
    
    print(f"Expected: {expected_total}, Actual: {cost_data['cost']}")
    assert abs(cost_data["cost"] - expected_total) < 1.0  # Allow for small differences


def test_calculate_workflow_cost_with_global_volume_discount(client, token, workflow_billing_model):
    """Test workflow cost calculation with global volume discount"""
    headers = {"Authorization": f"Bearer {token}"}
    usage_data = {
        "workflows": {
            "lead_research": 30,
            "email_personalization": 25,
            # Total: 55 workflows (exceeds threshold of 50 for 20% discount)
        }
    }
    response = client.post(
        f"/api/v1/billing-models/{workflow_billing_model}/calculate",
        json=usage_data,
        headers=headers
    )
    assert response.status_code == 200
    cost_data = response.json()
    
    # Base cost: $3,000 + (30 * $1.80) + (25 * $0.90) = $3,076.50 (using volume tier 1 pricing)
    # Global discount: 20% off total cost = $3,076.50 * 0.8 = $2,461.20
    base_cost = 3000.0 + (30 * 1.80) + (25 * 0.90)
    expected_cost = base_cost * 0.8  # 20% discount
    
    print(f"Expected: {expected_cost}, Actual: {cost_data['cost']}")
    assert abs(cost_data["cost"] - expected_cost) < 1.0


def test_calculate_workflow_cost_with_commitment_exceeded(client, token, workflow_billing_model):
    """Test workflow cost calculation with overage multiplier"""
    headers = {"Authorization": f"Bearer {token}"}
    usage_data = {
        "workflows": {
            "lead_research": 10,
            "email_personalization": 5
        },
        "commitment_exceeded": True
    }
    response = client.post(
        f"/api/v1/billing-models/{workflow_billing_model}/calculate",
        json=usage_data,
        headers=headers
    )
    assert response.status_code == 200
    cost_data = response.json()
    
    # Base platform fee: $3,000 (not affected by overage)
    # Workflow costs: (10 * $1.80) + (5 * $0.90) = $22.50 (using volume tier 1 pricing)
    # With overage multiplier 1.0: $22.50 * 1.0 = $22.50
    # Total: $3,022.50
    expected_cost = 3000.0 + (10 * 1.80 * 1.0) + (5 * 0.90 * 1.0)
    print(f"Expected: {expected_cost}, Actual: {cost_data['cost']}")
    assert abs(cost_data["cost"] - expected_cost) < 1.0


def test_calculate_workflow_cost_minimum_charge(client, token, workflow_billing_model):
    """Test workflow cost calculation with minimum charge enforcement"""
    headers = {"Authorization": f"Bearer {token}"}
    usage_data = {
        "workflows": {
            "meeting_booking": 1  # Has minimum charge of $8.00
        }
    }
    response = client.post(
        f"/api/v1/billing-models/{workflow_billing_model}/calculate",
        json=usage_data,
        headers=headers
    )
    assert response.status_code == 200
    cost_data = response.json()
    
    # Base platform fee: $3,000
    # Meeting booking: max(1 * $8.00, $8.00) = $8.00 (minimum charge applies)
    # Total: $3,008
    expected_cost = 3000.0 + 8.0
    assert cost_data["cost"] == expected_cost


def test_update_workflow_billing_model(client, token, workflow_billing_model):
    """Test updating a workflow-based billing model"""
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/api/v1/billing-models/{workflow_billing_model}",
        json={"name": UPDATED_NAME},
        headers=headers
    )
    assert response.status_code == 200
    bm = response.json()
    assert bm["name"] == UPDATED_NAME


def test_workflow_billing_model_validation_errors(client, token, setup_org):
    """Test validation errors for workflow-based billing models"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test missing workflow types and base fee
    invalid_data = {
        "name": "Invalid Workflow Model",
        "description": "This should fail validation",
        "model_type": "workflow",
        "organization_id": setup_org
    }
    response = client.post(
        "/api/v1/billing-models/",
        json=invalid_data,
        headers=headers
    )
    assert response.status_code == 400
    assert "must include at least a base config or one workflow type" in response.json()["detail"]
    
    # Test invalid workflow type data
    invalid_workflow_data = {
        "name": "Invalid Workflow Model 2",
        "description": "This should also fail validation",
        "model_type": "workflow",
        "organization_id": setup_org,
        "workflow_types": [
            {
                "workflow_name": "",  # Invalid: empty name
                "workflow_type": "test",
                "price_per_workflow": -10.0  # Invalid: negative price
            }
        ]
    }
    response = client.post(
        "/api/v1/billing-models/",
        json=invalid_workflow_data,
        headers=headers
    )
    assert response.status_code == 400
    assert "positive 'price_per_workflow' and 'workflow_name'" in response.json()["detail"]


def test_delete_workflow_billing_model(client, token, workflow_billing_model):
    """Test deleting a workflow-based billing model"""
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/api/v1/billing-models/{workflow_billing_model}", headers=headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(f"/api/v1/billing-models/{workflow_billing_model}", headers=headers)
    assert response.status_code == 404
