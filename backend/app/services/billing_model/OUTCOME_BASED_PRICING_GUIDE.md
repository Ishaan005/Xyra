# Outcome-Based Pricing Implementation Guide

## Overview

This document provides a comprehensive guide to implementing sophisticated outcome-based pricing in the Xyra AI agent billing system. Outcome-based pricing represents the pinnacle of value-aligned pricing and is the most resistant to commoditization.

## Design Principles

### 1. Results-Only Focus
- Charge only for achieved outcomes, not attempts
- Decouple pricing from underlying technology costs
- Align pricing with customer value delivered

### 2. Clear Attribution
- Develop robust methodologies to prove impact
- Track outcomes with attribution windows
- Support verification workflows

### 3. Shared Risk AND Reward
- Include performance guarantees with base platform fees
- Offer success bonuses for exceptional results
- Apply risk premiums to account for uncertainty

### 4. Premium Positioning
- Command highest prices through guaranteed results
- Support multi-tier pricing based on outcome value
- Enable monthly caps to prevent runaway costs

### 5. Future-Proof Model
- Most resistant to AI commoditization
- Maintains margins by focusing on value, not resources

## Database Models

### OutcomeBasedConfig
The enhanced outcome configuration supports:

```python
class OutcomeBasedConfig(BaseModel):
    # Outcome identification
    outcome_name: str              # e.g., "Revenue Uplift", "Cost Savings"
    outcome_type: str              # revenue_uplift, cost_savings, lead_generation
    description: str               # Detailed description
    
    # Base platform fee (operational costs coverage)
    base_platform_fee: float      # Monthly fee regardless of outcomes
    platform_fee_frequency: str   # monthly, yearly
    
    # Primary outcome pricing
    percentage: float              # Base percentage of outcome value
    
    # Attribution and verification
    attribution_window_days: int  # How long to attribute outcomes (default: 30)
    minimum_attribution_value: float # Minimum value to qualify for billing
    requires_verification: bool    # Whether outcomes need verification
    
    # Risk adjustment
    success_rate_assumption: float # Expected success rate (0.0-1.0)
    risk_premium_percentage: float # Risk premium (typically 30-50%)
    
    # Performance guarantees and caps
    monthly_cap_amount: float      # Maximum billing per month
    success_bonus_threshold: float # Value threshold for bonus
    success_bonus_percentage: float # Additional percentage for exceeding threshold
    
    # Multi-tier pricing
    tier_1_threshold: float        # First tier threshold
    tier_1_percentage: float       # Percentage for tier 1
    tier_2_threshold: float        # Second tier threshold
    tier_2_percentage: float       # Percentage for tier 2
    tier_3_threshold: float        # Third tier threshold
    tier_3_percentage: float       # Percentage for tier 3
```

### OutcomeMetric
Tracks individual outcome instances:

```python
class OutcomeMetric(BaseModel):
    outcome_value: float           # The measured outcome value
    attribution_start_date: datetime
    attribution_end_date: datetime
    verification_status: str      # pending, verified, rejected
    calculated_fee: float         # Fee calculated for this outcome
    tier_applied: str            # Which tier was applied
    bonus_applied: float         # Any bonus applied
    billing_status: str          # pending, ready, billed, disputed
```

## Implementation Examples

### Example 1: Recruiting Agent

```python
# Create outcome-based billing model for recruiting
billing_model = OutcomeBasedConfig(
    outcome_name="Successful Hire",
    outcome_type="recruiting",
    description="Payment for successful candidate placements",
    
    # Base fee to cover operational costs
    base_platform_fee=2000.0,  # $2,000/month platform access
    platform_fee_frequency="monthly",
    
    # Primary outcome pricing
    percentage=15.0,  # 15% of first-year salary
    
    # Attribution settings
    attribution_window_days=90,  # 90 days to attribute hires
    minimum_attribution_value=40000.0,  # Minimum $40k salary to qualify
    requires_verification=True,
    
    # Risk adjustment
    success_rate_assumption=0.70,  # 70% expected success rate
    risk_premium_percentage=40.0,  # 40% risk premium
    
    # Performance caps and bonuses
    monthly_cap_amount=50000.0,  # Max $50k/month
    success_bonus_threshold=100000.0,  # Bonus for $100k+ salaries
    success_bonus_percentage=2.0,  # Additional 2% for high-value hires
    
    # Multi-tier pricing
    tier_1_threshold=75000.0,     # Up to $75k salary
    tier_1_percentage=12.0,       # 12% for entry-level
    tier_2_threshold=125000.0,    # Up to $125k salary
    tier_2_percentage=15.0,       # 15% for mid-level
    tier_3_threshold=200000.0,    # Up to $200k salary
    tier_3_percentage=18.0,       # 18% for senior roles
)
```

### Example 2: E-commerce Optimization Agent

```python
# Create outcome-based billing for conversion optimization
billing_model = OutcomeBasedConfig(
    outcome_name="Revenue Increase",
    outcome_type="revenue_uplift",
    description="Payment based on incremental revenue generated",
    
    # Base fee for infrastructure
    base_platform_fee=500.0,  # $500/month for A/B testing infrastructure
    platform_fee_frequency="monthly",
    
    # Primary outcome pricing
    percentage=5.0,  # 5% of incremental revenue
    
    # Attribution settings
    attribution_window_days=30,  # 30 days attribution
    minimum_attribution_value=1000.0,  # Minimum $1k incremental revenue
    requires_verification=True,
    
    # Risk adjustment
    success_rate_assumption=0.80,  # 80% expected success rate
    risk_premium_percentage=30.0,  # 30% risk premium
    
    # Performance caps
    monthly_cap_amount=25000.0,  # Max $25k/month to prevent runaway costs
    
    # Tiered pricing for different revenue levels
    tier_1_threshold=10000.0,     # Up to $10k incremental revenue
    tier_1_percentage=3.0,        # 3% for small improvements
    tier_2_threshold=50000.0,     # Up to $50k incremental revenue
    tier_2_percentage=5.0,        # 5% for medium improvements
    tier_3_threshold=100000.0,    # Up to $100k incremental revenue
    tier_3_percentage=7.0,        # 7% for large improvements
)
```

## API Usage

### Recording Outcomes

```python
# Record an outcome for an agent
POST /api/v1/outcomes/record
{
    "agent_id": 123,
    "outcome_value": 75000.0,
    "outcome_currency": "USD",
    "attribution_start_date": "2025-01-01T00:00:00Z",
    "attribution_end_date": "2025-01-31T23:59:59Z",
    "outcome_data": {
        "candidate_id": "cand_456",
        "hire_date": "2025-01-15",
        "position": "Senior Developer",
        "annual_salary": 75000
    }
}
```

### Verifying Outcomes

```python
# Verify an outcome
POST /api/v1/outcomes/{outcome_id}/verify
{
    "verified_by": "user_789",
    "verification_status": "verified",
    "verification_notes": "Confirmed hire start date and salary"
}
```

### Getting Billing-Ready Outcomes

```python
# Get outcomes ready for billing
GET /api/v1/outcomes/billing-ready?agent_id=123&billing_period=2025-01
```

## Billing Calculation Logic

The enhanced calculation logic supports:

1. **Base Platform Fee**: Always charged regardless of outcomes
2. **Tiered Outcome Pricing**: Different percentages for different value ranges
3. **Risk Premium**: Additional percentage to account for success rate
4. **Success Bonuses**: Extra percentage for exceptional outcomes
5. **Monthly Caps**: Maximum billing amount per month
6. **Minimum Attribution**: Threshold below which no outcome fees are charged

### Example Calculation

For a $75,000 recruiting outcome with the configuration above:

```python
# Base platform fee: $2,000 (always charged)
base_fee = 2000.0

# Tier calculation (falls in tier_2: $75k <= $125k)
tier_fee = 75000.0 * 0.15  # 15% = $11,250

# Risk premium (40% of tier fee)
risk_premium = 11250.0 * 0.40  # = $4,500

# Total outcome fee
total_fee = base_fee + tier_fee + risk_premium  # = $17,750
```

## Best Practices

### 1. Start with Simple Configuration
- Begin with basic percentage-based pricing
- Add complexity (tiers, bonuses, caps) as you gain experience
- Monitor success rates and adjust risk premiums accordingly

### 2. Robust Verification
- Always require verification for high-value outcomes
- Implement multiple verification methods
- Use attribution windows appropriate for your use case

### 3. Risk Management
- Set appropriate monthly caps to prevent unexpected costs
- Use conservative success rate assumptions initially
- Adjust risk premiums based on actual performance data

### 4. Customer Communication
- Clearly communicate how outcomes are measured
- Provide transparent reporting on attribution and verification
- Set clear expectations about verification requirements

### 5. Continuous Optimization
- Monitor outcome statistics and success rates
- Adjust pricing tiers based on customer feedback
- Optimize attribution windows based on actual outcome patterns

## Integration with Xyra Client

The Xyra client library supports automatic outcome recording:

```python
from xyra_client import XyraClient

client = XyraClient(agent_id="your_agent_id")

# Record outcome automatically
await client.record_outcome(
    value=75000.0,
    currency="USD",
    details={"hire_confirmed": True, "position": "Senior Developer"}
)
```

This sophisticated outcome-based pricing implementation provides the foundation for building the most advanced and future-proof AI agent billing system, ensuring that pricing remains aligned with customer value even as AI technology costs continue to decrease.
