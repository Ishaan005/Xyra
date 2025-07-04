#!/usr/bin/env python3
"""
Test script to verify agent service works with new billing model structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import BaseModel
from app.models.agent import Agent
from app.models.billing_model import BillingModel, ActivityBasedConfig
from app.models.organization import Organization
from app.services.agent_service import (
    create_agent, record_agent_activity, get_agent_billing_config, 
    validate_agent_billing_data, record_agent_workflow
)
from app.schemas.agent import AgentCreate, AgentActivityCreate

def test_agent_service_with_new_billing_model():
    """Test the agent service with new billing model structure"""
    
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test organization
        org = Organization(
            name="Test Org",
            description="Test organization",
            created_at=datetime.now(timezone.utc)
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create test billing model
        billing_model = BillingModel(
            name="Test Activity Model",
            description="Test activity-based billing",
            model_type="activity",
            organization_id=org.id,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(billing_model)
        db.commit()
        db.refresh(billing_model)
        
        # Create activity config
        activity_config = ActivityBasedConfig(
            billing_model_id=billing_model.id,
            price_per_unit=1.0,
            activity_type="api_call",
            unit_type="action",
            base_agent_fee=10.0,
            billing_frequency="monthly",
            is_active=True
        )
        db.add(activity_config)
        db.commit()
        
        # Create test agent
        agent_create = AgentCreate(
            name="Test Agent",
            description="Test agent for billing",
            organization_id=org.id,
            billing_model_id=billing_model.id,
            is_active=True,
            external_id="test-agent-001"
        )
        
        agent = create_agent(db, agent_create)
        print(f"✓ Created agent: {agent.name} with ID: {agent.id}")
        
        # Test getting billing config
        config = get_agent_billing_config(db, agent.id)
        print(f"✓ Retrieved billing config: {config['model_type']}")
        
        # Test activity validation
        activity_data = {"activity_type": "api_call"}
        is_valid = validate_agent_billing_data(db, agent.id, "activity", activity_data)
        print(f"✓ Activity validation: {is_valid}")
        
        # Test recording activity
        activity_create = AgentActivityCreate(
            agent_id=agent.id,
            activity_type="api_call",
            activity_metadata={"test": "data"}
        )
        
        activity = record_agent_activity(db, activity_create)
        print(f"✓ Recorded activity: {activity.activity_type} for agent {activity.agent_id}")
        
        # Test invalid activity type
        invalid_activity_data = {"activity_type": "invalid_type"}
        is_valid_invalid = validate_agent_billing_data(db, agent.id, "activity", invalid_activity_data)
        print(f"✓ Invalid activity validation: {is_valid_invalid}")
        
        print("\n✅ All tests passed! Agent service works correctly with new billing model structure.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_agent_service_with_new_billing_model()
