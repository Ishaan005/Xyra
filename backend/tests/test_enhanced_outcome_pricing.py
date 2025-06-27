"""
Test the enhanced outcome-based pricing functionality
"""
import pytest
from app.services.billing_model.calculation import calculate_cost
from app.models.billing_model import BillingModel, OutcomeBasedConfig


def test_enhanced_outcome_calculation():
    """Test enhanced outcome-based pricing calculation"""
    
    # Create a mock billing model with enhanced outcome configuration
    billing_model = BillingModel()
    setattr(billing_model, 'model_type', "outcome")
    
    # Create enhanced outcome config
    outcome_config = OutcomeBasedConfig()
    
    # Set attributes using setattr to avoid SQLAlchemy Column issues
    setattr(outcome_config, 'is_active', True)
    setattr(outcome_config, 'base_platform_fee', 2000.0)
    setattr(outcome_config, 'percentage', 15.0)
    setattr(outcome_config, 'minimum_attribution_value', 1000.0)
    setattr(outcome_config, 'risk_premium_percentage', 40.0)
    setattr(outcome_config, 'monthly_cap_amount', 50000.0)
    setattr(outcome_config, 'success_bonus_threshold', 100000.0)
    setattr(outcome_config, 'success_bonus_percentage', 2.0)
    
    # Tiered pricing
    setattr(outcome_config, 'tier_1_threshold', 50000.0)
    setattr(outcome_config, 'tier_1_percentage', 12.0)
    setattr(outcome_config, 'tier_2_threshold', 100000.0)
    setattr(outcome_config, 'tier_2_percentage', 15.0)
    setattr(outcome_config, 'tier_3_threshold', 200000.0)
    setattr(outcome_config, 'tier_3_percentage', 18.0)
    
    # Mock the relationship
    billing_model.outcome_config = [outcome_config]
    
    # Test calculation with $75,000 outcome (falls in tier 2)
    usage_data = {"outcome_value": 75000.0}
    cost = calculate_cost(billing_model, usage_data)
    
    # Expected calculation:
    # Base platform fee: $2,000
    # Tier 1 (up to $50k): $50,000 * 12% = $6,000
    # Tier 2 (remaining $25k): $25,000 * 15% = $3,750
    # Total outcome fee: $9,750
    # Risk premium (40%): $9,750 * 40% = $3,900
    # Success bonus (not applicable, under $100k threshold)
    # Total: $2,000 + $9,750 + $3,900 = $15,650
    
    expected_cost = 2000.0 + 9750.0 + 3900.0  # = $15,650
    assert abs(cost - expected_cost) < 0.01, f"Expected {expected_cost}, got {cost}"


def test_outcome_calculation_with_bonus():
    """Test outcome calculation with success bonus"""
    
    billing_model = BillingModel()
    setattr(billing_model, 'model_type', "outcome")
    
    outcome_config = OutcomeBasedConfig()
    setattr(outcome_config, 'is_active', True)
    setattr(outcome_config, 'base_platform_fee', 500.0)
    setattr(outcome_config, 'percentage', 5.0)
    setattr(outcome_config, 'minimum_attribution_value', None)
    setattr(outcome_config, 'risk_premium_percentage', 30.0)
    setattr(outcome_config, 'monthly_cap_amount', None)
    setattr(outcome_config, 'success_bonus_threshold', 50000.0)
    setattr(outcome_config, 'success_bonus_percentage', 2.0)
    
    # No tiered pricing for this test
    setattr(outcome_config, 'tier_1_threshold', None)
    
    billing_model.outcome_config = [outcome_config]
    
    # Test with $60,000 outcome (exceeds bonus threshold)
    usage_data = {"outcome_value": 60000.0}
    cost = calculate_cost(billing_model, usage_data)
    
    # Expected calculation:
    # Base platform fee: $500
    # Outcome fee: $60,000 * 5% = $3,000
    # Risk premium: $3,000 * 30% = $900
    # Success bonus: $60,000 * 2% = $1,200 (exceeds $50k threshold)
    # Total: $500 + $3,000 + $900 + $1,200 = $5,600
    
    expected_cost = 500.0 + 3000.0 + 900.0 + 1200.0
    assert abs(cost - expected_cost) < 0.01, f"Expected {expected_cost}, got {cost}"


def test_outcome_calculation_with_monthly_cap():
    """Test outcome calculation with monthly cap"""
    
    billing_model = BillingModel()
    setattr(billing_model, 'model_type', "outcome")
    
    outcome_config = OutcomeBasedConfig()
    setattr(outcome_config, 'is_active', True)
    setattr(outcome_config, 'base_platform_fee', 1000.0)
    setattr(outcome_config, 'percentage', 10.0)
    setattr(outcome_config, 'minimum_attribution_value', None)
    setattr(outcome_config, 'risk_premium_percentage', 0.0)  # No risk premium for simplicity
    setattr(outcome_config, 'monthly_cap_amount', 8000.0)
    setattr(outcome_config, 'success_bonus_threshold', None)
    setattr(outcome_config, 'tier_1_threshold', None)
    
    billing_model.outcome_config = [outcome_config]
    
    # Test with high outcome value that would exceed cap
    usage_data = {"outcome_value": 100000.0}
    cost = calculate_cost(billing_model, usage_data)
    
    # Expected calculation:
    # Base platform fee: $1,000
    # Outcome fee before cap: $100,000 * 10% = $10,000
    # Total before cap: $1,000 + $10,000 = $11,000
    # Monthly cap applied: $8,000 (total capped amount)
    
    expected_cost = 8000.0  # Total capped at monthly limit
    assert abs(cost - expected_cost) < 0.01, f"Expected {expected_cost}, got {cost}"


def test_outcome_calculation_below_minimum():
    """Test outcome calculation below minimum attribution value"""
    
    billing_model = BillingModel()
    setattr(billing_model, 'model_type', "outcome")
    
    outcome_config = OutcomeBasedConfig()
    setattr(outcome_config, 'is_active', True)
    setattr(outcome_config, 'base_platform_fee', 1000.0)
    setattr(outcome_config, 'percentage', 5.0)
    setattr(outcome_config, 'minimum_attribution_value', 5000.0)
    setattr(outcome_config, 'risk_premium_percentage', 0.0)
    setattr(outcome_config, 'monthly_cap_amount', None)
    setattr(outcome_config, 'success_bonus_threshold', None)
    setattr(outcome_config, 'tier_1_threshold', None)
    
    billing_model.outcome_config = [outcome_config]
    
    # Test with outcome below minimum threshold
    usage_data = {"outcome_value": 3000.0}
    cost = calculate_cost(billing_model, usage_data)
    
    # Expected: Only platform fee, no outcome fee
    expected_cost = 1000.0
    assert abs(cost - expected_cost) < 0.01, f"Expected {expected_cost}, got {cost}"


if __name__ == "__main__":
    test_enhanced_outcome_calculation()
    test_outcome_calculation_with_bonus()
    test_outcome_calculation_with_monthly_cap()
    test_outcome_calculation_below_minimum()
    print("All enhanced outcome-based pricing tests passed!")
