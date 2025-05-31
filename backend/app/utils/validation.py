"""
Data Validation Framework for Xyra Platform

Provides comprehensive data validation capabilities including:
- Schema validation for various data formats
- Data type checking and coercion
- Business rule validation
- Constraint enforcement
- Detailed error reporting

Designed for the AI agent monetization platform to ensure data quality
across billing, analytics, and integration workflows.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from decimal import Decimal
import re
import json
from enum import Enum
from dataclasses import dataclass
import pandas as pd
from pydantic import ValidationError as PydanticValidationError, validator
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Validation error severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class DataType(str, Enum):
    """Supported data types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    URL = "url"
    JSON = "json"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    UUID = "uuid"


@dataclass
class ValidationError:
    """Represents a validation error with context"""
    field: str
    message: str
    severity: ValidationSeverity
    code: str
    value: Any = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    cleaned_data: Optional[Dict[str, Any]] = None
    
    @property
    def has_errors(self) -> bool:
        return bool(self.errors)
    
    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of errors by severity"""
        return {
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "total_issues": len(self.errors) + len(self.warnings)
        }


class ValidationRule:
    """Base class for validation rules"""
    
    def __init__(self, name: str, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.name = name
        self.message = message
        self.severity = severity
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationError]:
        """Validate a value against this rule"""
        raise NotImplementedError


class RequiredRule(ValidationRule):
    """Validates that a field is not empty/null"""
    
    def __init__(self):
        super().__init__("required", "Field is required", ValidationSeverity.ERROR)
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationError]:
        if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
            return ValidationError(
                field=context.get("field", "unknown") if context else "unknown",
                message=self.message,
                severity=self.severity,
                code=self.name,
                value=value
            )
        return None


class DataTypeRule(ValidationRule):
    """Validates data type and optionally converts it"""
    
    def __init__(self, data_type: DataType, allow_coercion: bool = True):
        self.data_type = data_type
        self.allow_coercion = allow_coercion
        super().__init__(
            f"type_{data_type.value}",
            f"Value must be of type {data_type.value}",
            ValidationSeverity.ERROR
        )
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationError]:
        field = context.get("field", "unknown") if context else "unknown"
        
        if value is None:
            return None
        
        try:
            converted_value = self._convert_value(value)
            if context and self.allow_coercion:
                context["converted_value"] = converted_value
            return None
        except (ValueError, TypeError) as e:
            return ValidationError(
                field=field,
                message=f"{self.message}: {str(e)}",
                severity=self.severity,
                code=self.name,
                value=value
            )
    
    def _convert_value(self, value: Any) -> Any:
        """Convert value to the expected type"""
        if self.data_type == DataType.STRING:
            return str(value)
        elif self.data_type == DataType.INTEGER:
            return int(value)
        elif self.data_type == DataType.FLOAT:
            return float(value)
        elif self.data_type == DataType.DECIMAL:
            return Decimal(str(value))
        elif self.data_type == DataType.BOOLEAN:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)
        elif self.data_type == DataType.DATE:
            if isinstance(value, str):
                return datetime.strptime(value, "%Y-%m-%d").date()
            elif isinstance(value, datetime):
                return value.date()
            return value
        elif self.data_type == DataType.DATETIME:
            if isinstance(value, str):
                # Try multiple datetime formats
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Unable to parse datetime: {value}")
            return value
        elif self.data_type == DataType.EMAIL:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(value)):
                raise ValueError("Invalid email format")
            return str(value)
        elif self.data_type == DataType.URL:
            url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
            if not re.match(url_pattern, str(value)):
                raise ValueError("Invalid URL format")
            return str(value)
        elif self.data_type == DataType.JSON:
            if isinstance(value, str):
                return json.loads(value)
            return value
        elif self.data_type == DataType.CURRENCY:
            # Remove currency symbols and convert to decimal
            currency_str = str(value).replace("$", "").replace(",", "")
            return Decimal(currency_str)
        elif self.data_type == DataType.PERCENTAGE:
            # Handle percentage values
            percent_str = str(value).replace("%", "")
            return float(percent_str) / 100 if "%" in str(value) else float(percent_str)
        elif self.data_type == DataType.UUID:
            import uuid
            if isinstance(value, str):
                return uuid.UUID(value)
            return value
        
        return value


class RangeRule(ValidationRule):
    """Validates that a value is within a specified range"""
    
    def __init__(self, min_value: Optional[Union[int, float]] = None, 
                 max_value: Optional[Union[int, float]] = None):
        self.min_value = min_value
        self.max_value = max_value
        name = f"range_{min_value}_{max_value}"
        message = f"Value must be between {min_value} and {max_value}"
        super().__init__(name, message, ValidationSeverity.ERROR)
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationError]:
        field = context.get("field", "unknown") if context else "unknown"
        
        if value is None:
            return None
        
        try:
            numeric_value = float(value)
            
            if self.min_value is not None and numeric_value < self.min_value:
                return ValidationError(
                    field=field,
                    message=f"Value {numeric_value} is less than minimum {self.min_value}",
                    severity=self.severity,
                    code=self.name,
                    value=value
                )
            
            if self.max_value is not None and numeric_value > self.max_value:
                return ValidationError(
                    field=field,
                    message=f"Value {numeric_value} is greater than maximum {self.max_value}",
                    severity=self.severity,
                    code=self.name,
                    value=value
                )
            
            return None
        except (ValueError, TypeError):
            return ValidationError(
                field=field,
                message="Value must be numeric for range validation",
                severity=self.severity,
                code=self.name,
                value=value
            )


class RegexRule(ValidationRule):
    """Validates that a value matches a regular expression pattern"""
    
    def __init__(self, pattern: str, message: Optional[str] = None):
        self.pattern = pattern
        self.regex = re.compile(pattern)
        name = f"regex_{hash(pattern)}"
        default_message = f"Value must match pattern: {pattern}"
        super().__init__(name, message or default_message, ValidationSeverity.ERROR)
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationError]:
        field = context.get("field", "unknown") if context else "unknown"
        
        if value is None:
            return None
        
        if not self.regex.match(str(value)):
            return ValidationError(
                field=field,
                message=self.message,
                severity=self.severity,
                code=self.name,
                value=value
            )
        
        return None


class CustomRule(ValidationRule):
    """Validates using a custom function"""
    
    def __init__(self, validator_func: Callable[[Any], Union[bool, str]], 
                 name: str, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.validator_func = validator_func
        super().__init__(name, message, severity)
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationError]:
        field = context.get("field", "unknown") if context else "unknown"
        
        try:
            result = self.validator_func(value)
            
            if isinstance(result, bool):
                if not result:
                    return ValidationError(
                        field=field,
                        message=self.message,
                        severity=self.severity,
                        code=self.name,
                        value=value
                    )
            elif isinstance(result, str):
                # Return custom error message
                return ValidationError(
                    field=field,
                    message=result,
                    severity=self.severity,
                    code=self.name,
                    value=value
                )
            
            return None
        except Exception as e:
            return ValidationError(
                field=field,
                message=f"Custom validation failed: {str(e)}",
                severity=self.severity,
                code=self.name,
                value=value
            )


class BusinessRule(ValidationRule):
    """Validates business-specific rules"""
    
    def __init__(self, rule_name: str, rule_func: Callable[[Any, Dict[str, Any]], Union[bool, str]], 
                 message: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.rule_func = rule_func
        super().__init__(f"business_{rule_name}", message, severity)
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> Optional[ValidationError]:
        field = context.get("field", "unknown") if context else "unknown"
        
        try:
            # Business rules get the full data context
            data_context = context.get("data", {}) if context else {}
            result = self.rule_func(value, data_context)
            
            if isinstance(result, bool):
                if not result:
                    return ValidationError(
                        field=field,
                        message=self.message,
                        severity=self.severity,
                        code=self.name,
                        value=value,
                        context=data_context
                    )
            elif isinstance(result, str):
                return ValidationError(
                    field=field,
                    message=result,
                    severity=self.severity,
                    code=self.name,
                    value=value,
                    context=data_context
                )
            
            return None
        except Exception as e:
            return ValidationError(
                field=field,
                message=f"Business rule validation failed: {str(e)}",
                severity=self.severity,
                code=self.name,
                value=value
            )


class FieldSchema:
    """Schema definition for a single field"""
    
    def __init__(self, field_name: str, rules: Optional[List[ValidationRule]] = None):
        self.field_name = field_name
        self.rules = rules or []
    
    def add_rule(self, rule: ValidationRule) -> "FieldSchema":
        """Add a validation rule to this field"""
        self.rules.append(rule)
        return self
    
    def required(self) -> "FieldSchema":
        """Make this field required"""
        return self.add_rule(RequiredRule())
    
    def type(self, data_type: DataType, allow_coercion: bool = True) -> "FieldSchema":
        """Set the data type for this field"""
        return self.add_rule(DataTypeRule(data_type, allow_coercion))
    
    def range(self, min_value: Optional[Union[int, float]] = None, 
              max_value: Optional[Union[int, float]] = None) -> "FieldSchema":
        """Add range validation"""
        return self.add_rule(RangeRule(min_value, max_value))
    
    def regex(self, pattern: str, message: Optional[str] = None) -> "FieldSchema":
        """Add regex validation"""
        return self.add_rule(RegexRule(pattern, message))
    
    def custom(self, validator_func: Callable[[Any], Union[bool, str]], 
               name: str, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> "FieldSchema":
        """Add custom validation"""
        return self.add_rule(CustomRule(validator_func, name, message, severity))
    
    def business(self, rule_name: str, rule_func: Callable[[Any, Dict[str, Any]], Union[bool, str]], 
                 message: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> "FieldSchema":
        """Add business rule validation"""
        return self.add_rule(BusinessRule(rule_name, rule_func, message, severity))


class DataValidator:
    """Main data validation engine"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, FieldSchema]] = {}
        self.global_rules: List[ValidationRule] = []
    
    def create_schema(self, schema_name: str) -> "SchemaBuilder":
        """Create a new validation schema"""
        self.schemas[schema_name] = {}
        return SchemaBuilder(self, schema_name)
    
    def validate(self, data: Dict[str, Any], schema_name: str, 
                 strict: bool = False) -> ValidationResult:
        """Validate data against a schema"""
        if schema_name not in self.schemas:
            raise ValueError(f"Schema '{schema_name}' not found")
        
        schema = self.schemas[schema_name]
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Track which fields have been validated
        validated_fields = set()
        
        # Validate defined fields
        for field_name, field_schema in schema.items():
            value = data.get(field_name)
            context = {
                "field": field_name,
                "data": data,
                "schema": schema_name
            }
            
            for rule in field_schema.rules:
                error = rule.validate(value, context)
                if error:
                    if error.severity == ValidationSeverity.ERROR:
                        errors.append(error)
                    else:
                        warnings.append(error)
                
                # Handle type coercion
                if ("converted_value" in context and 
                    not error and 
                    isinstance(rule, DataTypeRule) and 
                    rule.allow_coercion):
                    cleaned_data[field_name] = context["converted_value"]
                elif field_name not in cleaned_data:
                    cleaned_data[field_name] = value
            
            validated_fields.add(field_name)
        
        # In strict mode, flag unexpected fields
        if strict:
            for field_name, value in data.items():
                if field_name not in validated_fields:
                    warnings.append(ValidationError(
                        field=field_name,
                        message=f"Unexpected field in schema '{schema_name}'",
                        severity=ValidationSeverity.WARNING,
                        code="unexpected_field",
                        value=value
                    ))
        
        # Apply global rules
        for rule in self.global_rules:
            error = rule.validate(data, {"schema": schema_name})
            if error:
                if error.severity == ValidationSeverity.ERROR:
                    errors.append(error)
                else:
                    warnings.append(error)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data if len(errors) == 0 else None
        )
    
    def validate_dataframe(self, df: pd.DataFrame, schema_name: str, 
                          strict: bool = False) -> List[ValidationResult]:
        """Validate a pandas DataFrame row by row"""
        results = []
        
        for index, row in df.iterrows():
            row_data = row.to_dict()
            row_data["_row_index"] = index
            result = self.validate(row_data, schema_name, strict)
            results.append(result)
        
        return results
    
    def add_global_rule(self, rule: ValidationRule):
        """Add a global validation rule that applies to all schemas"""
        self.global_rules.append(rule)
    
    def get_rules_by_type(self, validation_type: str) -> List[Dict[str, Any]]:
        """Get validation rules filtered by type"""
        rules = []
        if validation_type in self.schemas:
            schema = self.schemas[validation_type]
            for field_name, field_schema in schema.items():
                for rule in field_schema.rules:
                    rules.append({
                        "rule_name": rule.name,
                        "field": field_name,
                        "validation_type": validation_type,
                        "required": isinstance(rule, RequiredRule),
                        "description": getattr(rule, 'message', ''),
                        "severity": rule.severity.value
                    })
        return rules
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Get all validation rules across all schemas"""
        all_rules = []
        for schema_name in self.schemas:
            all_rules.extend(self.get_rules_by_type(schema_name))
        return all_rules


class SchemaBuilder:
    """Builder for creating validation schemas"""
    
    def __init__(self, validator: DataValidator, schema_name: str):
        self.validator = validator
        self.schema_name = schema_name
    
    def field(self, field_name: str) -> "SchemaBuilder":
        """Define a field in the schema"""
        field_schema = FieldSchema(field_name)
        self.validator.schemas[self.schema_name][field_name] = field_schema
        self._current_field = field_schema
        return self
    
    def required(self) -> "SchemaBuilder":
        """Make the current field required"""
        if hasattr(self, '_current_field'):
            self._current_field.required()
        return self
    
    def type(self, data_type: DataType, allow_coercion: bool = True) -> "SchemaBuilder":
        """Set the data type for the current field"""
        if hasattr(self, '_current_field'):
            self._current_field.type(data_type, allow_coercion)
        return self
    
    def range(self, min_value: Optional[Union[int, float]] = None, 
              max_value: Optional[Union[int, float]] = None) -> "SchemaBuilder":
        """Add range validation to the current field"""
        if hasattr(self, '_current_field'):
            self._current_field.range(min_value, max_value)
        return self
    
    def regex(self, pattern: str, message: Optional[str] = None) -> "SchemaBuilder":
        """Add regex validation to the current field"""
        if hasattr(self, '_current_field'):
            self._current_field.regex(pattern, message)
        return self
    
    def custom(self, validator_func: Callable[[Any], Union[bool, str]], 
               name: str, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> "SchemaBuilder":
        """Add custom validation to the current field"""
        if hasattr(self, '_current_field'):
            self._current_field.custom(validator_func, name, message, severity)
        return self
    
    def business(self, rule_name: str, rule_func: Callable[[Any, Dict[str, Any]], Union[bool, str]], 
                 message: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> "SchemaBuilder":
        """Add business rule validation to the current field"""
        if hasattr(self, '_current_field'):
            self._current_field.business(rule_name, rule_func, message, severity)
        return self
    
    def build(self) -> DataValidator:
        """Return the validator instance"""
        return self.validator


# Predefined business rules for the Xyra platform
class XyraBusinessRules:
    """Business rules specific to the Xyra AI monetization platform"""
    
    @staticmethod
    def valid_billing_model_type(value: Any, context: Dict[str, Any]) -> bool:
        """Validate billing model type"""
        valid_types = ["seat", "activity", "outcome", "hybrid"]
        return value in valid_types
    
    @staticmethod
    def valid_currency_code(value: Any, context: Dict[str, Any]) -> bool:
        """Validate currency code"""
        valid_currencies = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY"]
        return value in valid_currencies
    
    @staticmethod
    def positive_amount(value: Any, context: Dict[str, Any]) -> bool:
        """Ensure monetary amounts are positive"""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def valid_agent_status(value: Any, context: Dict[str, Any]) -> bool:
        """Validate agent status"""
        valid_statuses = ["active", "inactive", "suspended", "archived"]
        return value in valid_statuses
    
    @staticmethod
    def valid_organization_status(value: Any, context: Dict[str, Any]) -> bool:
        """Validate organization status"""
        valid_statuses = ["active", "suspended", "trial", "archived"]
        return value in valid_statuses
    
    @staticmethod
    def outcome_value_matches_type(value: Any, context: Dict[str, Any]) -> Union[bool, str]:
        """Ensure outcome value is appropriate for the outcome type"""
        outcome_type = context.get("outcome_type")
        
        if not outcome_type:
            return True  # Can't validate without type
        
        try:
            numeric_value = float(value)
            
            if outcome_type in ["revenue_uplift", "cost_savings"] and numeric_value < 0:
                return "Revenue uplift and cost savings must be positive values"
            
            if outcome_type == "percentage_improvement" and (numeric_value < 0 or numeric_value > 1):
                return "Percentage improvement must be between 0 and 1"
            
            return True
        except (ValueError, TypeError):
            return "Outcome value must be numeric"
    
    @staticmethod
    def billing_frequency_valid(value: Any, context: Dict[str, Any]) -> bool:
        """Validate billing frequency"""
        valid_frequencies = ["monthly", "quarterly", "yearly", "daily", "weekly"]
        return value in valid_frequencies


# Factory function to create common validation schemas
def create_xyra_schemas() -> DataValidator:
    """Create standard validation schemas for the Xyra platform"""
    validator = DataValidator()
    
    # Agent validation schema
    (validator.create_schema("agent")
     .field("name").required().type(DataType.STRING)
     .field("description").type(DataType.STRING)
     .field("organization_id").required().type(DataType.INTEGER).range(min_value=1)
     .field("billing_model_id").type(DataType.INTEGER).range(min_value=1)
     .field("status").required().type(DataType.STRING).business(
         "valid_agent_status", 
         XyraBusinessRules.valid_agent_status,
         "Invalid agent status"
     )
     .field("type").type(DataType.STRING)
     .field("capabilities").type(DataType.JSON)
     .field("external_id").type(DataType.STRING))
    
    # Agent Activity validation schema
    (validator.create_schema("agent_activity")
     .field("agent_id").required().type(DataType.INTEGER).range(min_value=1)
     .field("activity_type").required().type(DataType.STRING)
     .field("timestamp").type(DataType.DATETIME)
     .field("activity_metadata").type(DataType.JSON))
    
    # Agent Cost validation schema
    (validator.create_schema("agent_cost")
     .field("agent_id").required().type(DataType.INTEGER).range(min_value=1)
     .field("cost_type").required().type(DataType.STRING)
     .field("amount").required().type(DataType.DECIMAL).business(
         "positive_amount",
         XyraBusinessRules.positive_amount,
         "Cost amount must be positive"
     )
     .field("currency").required().type(DataType.STRING).business(
         "valid_currency",
         XyraBusinessRules.valid_currency_code,
         "Invalid currency code"
     )
     .field("timestamp").type(DataType.DATETIME)
     .field("details").type(DataType.JSON))
    
    # Agent Outcome validation schema
    (validator.create_schema("agent_outcome")
     .field("agent_id").required().type(DataType.INTEGER).range(min_value=1)
     .field("outcome_type").required().type(DataType.STRING)
     .field("value").required().type(DataType.DECIMAL).business(
         "outcome_value_matches_type",
         XyraBusinessRules.outcome_value_matches_type,
         "Outcome value invalid for type"
     )
     .field("currency").required().type(DataType.STRING).business(
         "valid_currency",
         XyraBusinessRules.valid_currency_code,
         "Invalid currency code"
     )
     .field("timestamp").type(DataType.DATETIME)
     .field("verified").type(DataType.BOOLEAN)
     .field("details").type(DataType.JSON))
    
    # Organization validation schema
    (validator.create_schema("organization")
     .field("name").required().type(DataType.STRING)
     .field("description").type(DataType.STRING)
     .field("external_id").type(DataType.STRING)
     .field("status").required().type(DataType.STRING).business(
         "valid_org_status",
         XyraBusinessRules.valid_organization_status,
         "Invalid organization status"
     )
     .field("billing_email").type(DataType.EMAIL)
     .field("contact_name").type(DataType.STRING)
     .field("contact_phone").type(DataType.STRING).regex(
         r'^\+?1?-?\.?\s?\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})$',
         "Invalid phone number format"
     )
     .field("timezone").type(DataType.STRING)
     .field("settings").type(DataType.JSON))
    
    # Billing Model validation schema
    (validator.create_schema("billing_model")
     .field("name").required().type(DataType.STRING)
     .field("description").type(DataType.STRING)
     .field("organization_id").required().type(DataType.INTEGER).range(min_value=1)
     .field("model_type").required().type(DataType.STRING).business(
         "valid_billing_type",
         XyraBusinessRules.valid_billing_model_type,
         "Invalid billing model type"
     )
     .field("config").required().type(DataType.JSON)
     .field("is_active").type(DataType.BOOLEAN))
    
    # Integration Event validation schema
    (validator.create_schema("integration_event")
     .field("organization_id").required().type(DataType.INTEGER).range(min_value=1)
     .field("event_type").required().type(DataType.STRING)
     .field("event_source").required().type(DataType.STRING)
     .field("timestamp").required().type(DataType.DATETIME)
     .field("raw_data").required().type(DataType.JSON)
     .field("processed_data").type(DataType.JSON)
     .field("processing_status").type(DataType.STRING)
     .field("agent_id").type(DataType.INTEGER).range(min_value=1))
    
    logger.info("Created Xyra validation schemas")
    return validator


# Example usage and testing
if __name__ == "__main__":
    # Create validator with Xyra schemas
    validator = create_xyra_schemas()
    
    # Test agent validation
    agent_data = {
        "name": "Customer Support AI",
        "description": "AI agent for customer support",
        "organization_id": 1,
        "billing_model_id": 2,
        "status": "active",
        "type": "conversational",
        "capabilities": ["chat", "email", "knowledge_base"],
        "external_id": "cs-ai-001"
    }
    
    result = validator.validate(agent_data, "agent")
    print(f"Agent validation result: {result.is_valid}")
    if result.errors:
        for error in result.errors:
            print(f"Error: {error.field} - {error.message}")
    
    # Test with invalid data
    invalid_agent = {
        "name": "",  # Required field empty
        "organization_id": "not_a_number",  # Wrong type
        "status": "invalid_status",  # Invalid business rule
        "billing_model_id": -1  # Negative value
    }
    
    result = validator.validate(invalid_agent, "agent")
    print(f"\nInvalid agent validation result: {result.is_valid}")
    for error in result.errors:
        print(f"Error: {error.field} - {error.message}")
