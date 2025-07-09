#!/usr/bin/env python3
"""
Test script to verify billing model creation and editing functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Test data for different billing model types
test_models = {
    "activity": {
        "name": "Test Activity Model",
        "description": "A test activity-based billing model",
        "model_type": "activity",
        "activity_price_per_unit": 0.50,
        "activity_activity_type": "api_call",
        "activity_unit_type": "request",
        "activity_base_agent_fee": 100.0,
        "activity_volume_pricing_enabled": True,
        "activity_volume_tier_1_threshold": 1000,
        "activity_volume_tier_1_price": 0.45,
        "activity_volume_tier_2_threshold": 5000,
        "activity_volume_tier_2_price": 0.40,
        "activity_minimum_charge": 50.0,
        "activity_billing_frequency": "monthly",
        "activity_is_active": True,
        "organization_id": 1,
        "is_active": True
    },
    "outcome": {
        "name": "Test Outcome Model",
        "description": "A test outcome-based billing model",
        "model_type": "outcome",
        "outcome_outcome_name": "Lead Generation",
        "outcome_outcome_type": "lead_generation",
        "outcome_description": "Pay per qualified lead generated",
        "outcome_percentage": 15.0,
        "outcome_fixed_charge_per_outcome": 25.0,
        "outcome_currency": "USD",
        "outcome_billing_frequency": "monthly",
        "outcome_base_platform_fee": 500.0,
        "outcome_is_active": True,
        "organization_id": 1,
        "is_active": True
    },
    "agent": {
        "name": "Test Agent Model",
        "description": "A test agent-based billing model",
        "model_type": "agent",
        "agent_base_agent_fee": 299.0,
        "agent_billing_frequency": "monthly",
        "agent_setup_fee": 500.0,
        "agent_volume_discount_enabled": True,
        "agent_volume_discount_threshold": 10,
        "agent_volume_discount_percentage": 10.0,
        "agent_tier": "professional",
        "organization_id": 1,
        "is_active": True
    }
}

def create_billing_model(model_type, data):
    """Create a billing model"""
    print(f"\n=== Creating {model_type} billing model ===")
    response = requests.post(f"{BASE_URL}/billing-models", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        model = response.json()
        print(f"Created model ID: {model['id']}")
        print(f"Model name: {model['name']}")
        return model
    else:
        print(f"Error: {response.text}")
        return None

def get_billing_model(model_id):
    """Get a billing model by ID"""
    print(f"\n=== Fetching billing model {model_id} ===")
    response = requests.get(f"{BASE_URL}/billing-models/{model_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        model = response.json()
        print(f"Retrieved model: {model['name']}")
        return model
    else:
        print(f"Error: {response.text}")
        return None

def update_billing_model(model_id, data):
    """Update a billing model"""
    print(f"\n=== Updating billing model {model_id} ===")
    response = requests.put(f"{BASE_URL}/billing-models/{model_id}", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        model = response.json()
        print(f"Updated model: {model['name']}")
        return model
    else:
        print(f"Error: {response.text}")
        return None

def list_billing_models():
    """List all billing models"""
    print(f"\n=== Listing all billing models ===")
    response = requests.get(f"{BASE_URL}/billing-models")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        models = response.json()
        print(f"Found {len(models)} models:")
        for model in models:
            print(f"  - ID: {model['id']}, Name: {model['name']}, Type: {model['model_type']}")
        return models
    else:
        print(f"Error: {response.text}")
        return []

def main():
    """Main test function"""
    print("=== Billing Model API Test ===")
    
    # List existing models
    list_billing_models()
    
    created_models = []
    
    # Create test models
    for model_type, data in test_models.items():
        model = create_billing_model(model_type, data)
        if model:
            created_models.append(model)
    
    # Test retrieval and updates
    for model in created_models:
        model_id = model['id']
        
        # Get the model
        retrieved_model = get_billing_model(model_id)
        
        if retrieved_model:
            # Test update
            update_data = retrieved_model.copy()
            update_data['description'] = f"Updated description at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            if retrieved_model['model_type'] == 'activity':
                update_data['activity_price_per_unit'] = 0.60  # Increase price
            elif retrieved_model['model_type'] == 'outcome':
                update_data['outcome_percentage'] = 20.0  # Increase percentage
            elif retrieved_model['model_type'] == 'agent':
                update_data['agent_base_agent_fee'] = 399.0  # Increase fee
            
            updated_model = update_billing_model(model_id, update_data)
    
    # List models again to see updates
    list_billing_models()
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main()
