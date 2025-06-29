# Outcome-Based Pricing Features

## Overview

The Xyra platform now includes comprehensive outcome-based pricing functionality that allows users to:
- Create outcome-based pricing models with advanced features
- Track and verify outcomes through a dedicated dashboard
- Automatically calculate billing fees based on actual performance
- Manage outcome verification workflows

## Features Implemented

### Backend Modularization
- **Modular Architecture**: Split billing model logic into focused submodules
  - `billing_model/crud.py` - Database operations
  - `billing_model/validation.py` - Input validation and business rules
  - `billing_model/calculation.py` - Pricing calculations
  - `billing_model/config.py` - Configuration management
  - `billing_model/outcome_tracking.py` - Outcome tracking and verification

### Enhanced Outcome-Based Pricing
- **Multi-Tier Pricing**: Support for different percentage rates based on outcome value ranges
- **Performance Bonuses**: Additional rewards for exceeding performance thresholds
- **Risk Premiums**: Adjustable risk-based pricing multipliers
- **Caps and Floors**: Minimum and maximum fee limits
- **Verification Workflows**: Manual and automated outcome verification
- **Billing Integration**: Seamless integration with existing billing systems

### Frontend Integration

#### Pricing Model Creation (`/app/pricing/page.tsx`)
- **Outcome-Based Form**: Dedicated form for creating outcome-based pricing models
- **Advanced Configuration**: Support for all outcome-based pricing features
- **Validation**: Real-time form validation and error handling
- **Integration**: Seamless integration with existing pricing model management

#### Outcome Tracking Dashboard (`/app/outcomes/page.tsx`)
- **Statistics Overview**: Key metrics and performance indicators
  - Total outcomes recorded
  - Total outcome value
  - Total calculated fees
  - Success rate (verified outcomes)
- **Filtering and Search**: Advanced filtering by agent, status, and search queries
- **Outcome Management**: 
  - Record new outcomes
  - Verify pending outcomes
  - View outcome details and history
- **Real-time Updates**: Live updates when outcomes are verified or recorded

### API Endpoints

#### Core Endpoints
- `POST /api/v1/outcomes/record` - Record new outcome
- `GET /api/v1/outcomes` - List outcomes with filtering
- `GET /api/v1/outcomes/statistics` - Get outcome statistics
- `POST /api/v1/outcomes/{id}/verify` - Verify outcome
- `GET /api/v1/outcomes/{id}` - Get specific outcome details

#### Billing Model Endpoints
- `POST /api/v1/billing-models` - Create billing model (supports outcome-based)
- `GET /api/v1/billing-models` - List billing models
- `POST /api/v1/billing-models/{id}/calculate` - Calculate fees

## Usage Examples

### Creating an Outcome-Based Pricing Model

```json
{
  "name": "Performance-Based Campaign",
  "model_type": "outcome_based",
  "config": {
    "outcome_based": {
      "base_fee_percentage": 5.0,
      "tiers": [
        {"min_value": 0, "max_value": 10000, "percentage": 5.0},
        {"min_value": 10000, "max_value": 50000, "percentage": 7.5},
        {"min_value": 50000, "percentage": 10.0}
      ],
      "risk_premium": 1.2,
      "performance_bonuses": [
        {"threshold": 25000, "bonus_percentage": 2.0},
        {"threshold": 100000, "bonus_percentage": 5.0}
      ],
      "fee_cap": 5000.0,
      "fee_floor": 100.0,
      "verification_required": true
    }
  }
}
```

### Recording an Outcome

```json
{
  "agent_id": 1,
  "outcome_value": 15000.0,
  "outcome_currency": "USD",
  "outcome_data": {
    "campaign_id": 123,
    "source": "google_ads",
    "conversion_type": "sale"
  },
  "verification_required": true
}
```

## Testing

Comprehensive test suite covering:
- Multi-tier pricing calculations
- Performance bonus calculations
- Risk premium applications
- Fee caps and floors
- Verification workflows
- Edge cases and error handling

Run tests with:
```bash
cd backend
pytest tests/test_enhanced_outcome_pricing.py -v
```

## Security Considerations

- **Authentication**: All endpoints require valid authentication
- **Authorization**: Users can only access their own outcomes and billing models
- **Input Validation**: Comprehensive validation of all input data
- **Data Integrity**: Consistent data handling and transaction management

## Performance Considerations

- **Efficient Filtering**: Optimized database queries with proper indexing
- **Pagination**: Support for large datasets with pagination
- **Caching**: Strategic caching of frequently accessed data
- **Async Operations**: Non-blocking operations for better user experience

## Future Enhancements

- **Advanced Analytics**: More detailed reporting and analytics
- **Automated Verification**: Integration with external verification services
- **Bulk Operations**: Support for bulk outcome recording and verification
- **Notifications**: Real-time notifications for outcome verification status
- **Export Functionality**: Export outcomes and billing data to various formats

## Configuration

The outcome-based pricing system is highly configurable through:
- Environment variables for system-wide settings
- Database configuration for model-specific settings
- UI configuration for user preferences

## Troubleshooting

Common issues and solutions:
- **Verification Failures**: Check outcome data format and verification requirements
- **Calculation Errors**: Verify tier configurations and fee limits
- **API Errors**: Check authentication tokens and request format
- **UI Issues**: Ensure all required UI components are properly imported

## Support

For issues or questions regarding outcome-based pricing:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check the test suite for usage examples
4. Contact the development team
