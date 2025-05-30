"""
Data Transformation Service for Xyra Platform

Provides comprehensive data transformation capabilities including:
- Field mapping and data structure conversion
- Data type coercion and formatting
- Business logic transformations
- Data normalization and standardization
- Integration with validation framework

Designed for the AI agent monetization platform to ensure consistent
data flow across billing, analytics, and integration workflows.
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from decimal import Decimal
import re
import json
from enum import Enum
from dataclasses import dataclass
import pandas as pd
from pydantic import BaseModel
import logging
from app.utils.validation import DataValidator, ValidationResult, DataType

logger = logging.getLogger(__name__)


class TransformationType(str, Enum):
    """Types of data transformations"""
    FIELD_MAPPING = "field_mapping"
    TYPE_CONVERSION = "type_conversion"
    VALUE_NORMALIZATION = "value_normalization"
    BUSINESS_LOGIC = "business_logic"
    AGGREGATION = "aggregation"
    ENRICHMENT = "enrichment"


class TransformationSeverity(str, Enum):
    """Transformation result severity levels"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class TransformationRule:
    """Defines a single transformation rule"""
    name: str
    transformation_type: TransformationType
    source_field: Optional[str] = None
    target_field: Optional[str] = None
    rule_function: Optional[Callable] = None
    parameters: Optional[Dict[str, Any]] = None
    condition: Optional[Callable] = None
    priority: int = 0
    description: str = ""

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class TransformationResult:
    """Result of a transformation operation"""
    success: bool
    severity: TransformationSeverity
    message: str
    transformed_data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class DataTransformationService:
    """
    Core data transformation service for the Xyra platform.
    Provides comprehensive transformation capabilities with integration
    to the validation framework.
    """

    def __init__(self, validation_framework: Optional[DataValidator] = None):
        self.validation_framework = validation_framework or DataValidator()
        self.transformation_rules: List[TransformationRule] = []
        self.field_mappings: Dict[str, str] = {}
        self.type_conversions: Dict[str, DataType] = {}
        
    def add_transformation_rule(self, rule: TransformationRule) -> None:
        """Add a transformation rule to the service"""
        self.transformation_rules.append(rule)
        self.transformation_rules.sort(key=lambda x: x.priority, reverse=True)
        
    def add_field_mapping(self, source_field: str, target_field: str) -> None:
        """Add a field mapping transformation"""
        self.field_mappings[source_field] = target_field
        
    def add_type_conversion(self, field: str, target_type: DataType) -> None:
        """Add a type conversion transformation"""
        self.type_conversions[field] = target_type

    def transform_data(
        self, 
        data: Dict[str, Any],
        rules: Optional[List[TransformationRule]] = None,
        validate_input: bool = True,
        validate_output: bool = True
    ) -> TransformationResult:
        """
        Transform data using specified rules or default rules
        
        Args:
            data: Input data to transform
            rules: Optional specific rules to apply
            validate_input: Whether to validate input data
            validate_output: Whether to validate output data
            
        Returns:
            TransformationResult with transformed data and metadata
        """
        try:
            # Input validation
            if validate_input:
                validation_result = self.validation_framework.validate(data, "default")
                if not validation_result.is_valid:
                    return TransformationResult(
                        success=False,
                        severity=TransformationSeverity.ERROR,
                        message="Input validation failed",
                        errors=[f"Validation error: {error.message}" for error in validation_result.errors]
                    )

            # Apply transformation rules
            rules_to_apply = rules or self.transformation_rules
            transformed_data = data.copy()
            warnings = []
            metadata = {
                "rules_applied": [],
                "transformations_count": 0,
                "processing_time": None
            }

            start_time = datetime.now()

            for rule in rules_to_apply:
                try:
                    if rule.condition and not rule.condition(transformed_data):
                        continue
                        
                    result = self._apply_transformation_rule(transformed_data, rule)
                    if result:
                        metadata["rules_applied"].append(rule.name)
                        metadata["transformations_count"] += 1
                        if result.get("warning"):
                            warnings.append(result["warning"])
                            
                except Exception as e:
                    logger.error(f"Error applying transformation rule {rule.name}: {str(e)}")
                    return TransformationResult(
                        success=False,
                        severity=TransformationSeverity.ERROR,
                        message=f"Failed to apply transformation rule: {rule.name}",
                        errors=[str(e)]
                    )

            # Apply default field mappings and type conversions
            transformed_data = self._apply_field_mappings(transformed_data)
            transformed_data = self._apply_type_conversions(transformed_data)

            processing_time = (datetime.now() - start_time).total_seconds()
            metadata["processing_time"] = processing_time

            # Output validation
            if validate_output:
                validation_result = self.validation_framework.validate(transformed_data, "default")
                if not validation_result.is_valid:
                    return TransformationResult(
                        success=False,
                        severity=TransformationSeverity.ERROR,
                        message="Output validation failed",
                        errors=[f"Output validation error: {error.message}" for error in validation_result.errors],
                        transformed_data=transformed_data
                    )

            return TransformationResult(
                success=True,
                severity=TransformationSeverity.WARNING if warnings else TransformationSeverity.SUCCESS,
                message="Data transformation completed successfully",
                transformed_data=transformed_data,
                warnings=warnings,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Data transformation failed: {str(e)}")
            return TransformationResult(
                success=False,
                severity=TransformationSeverity.ERROR,
                message="Data transformation failed",
                errors=[str(e)]
            )

    def _apply_transformation_rule(
        self, 
        data: Dict[str, Any], 
        rule: TransformationRule
    ) -> Optional[Dict[str, Any]]:
        """Apply a single transformation rule to data"""
        
        if rule.transformation_type == TransformationType.FIELD_MAPPING:
            return self._apply_field_mapping_rule(data, rule)
        elif rule.transformation_type == TransformationType.TYPE_CONVERSION:
            return self._apply_type_conversion_rule(data, rule)
        elif rule.transformation_type == TransformationType.VALUE_NORMALIZATION:
            return self._apply_normalization_rule(data, rule)
        elif rule.transformation_type == TransformationType.BUSINESS_LOGIC:
            return self._apply_business_logic_rule(data, rule)
        elif rule.transformation_type == TransformationType.AGGREGATION:
            return self._apply_aggregation_rule(data, rule)
        else:
            logger.warning(f"Unknown transformation type: {rule.transformation_type}")
            return None

    def _apply_field_mapping_rule(
        self, 
        data: Dict[str, Any], 
        rule: TransformationRule
    ) -> Dict[str, Any]:
        """Apply field mapping transformation"""
        if rule.source_field and rule.target_field:
            if rule.source_field in data:
                data[rule.target_field] = data[rule.source_field]
                if rule.target_field != rule.source_field:
                    del data[rule.source_field]
        return {}

    def _apply_type_conversion_rule(
        self, 
        data: Dict[str, Any], 
        rule: TransformationRule
    ) -> Dict[str, Any]:
        """Apply type conversion transformation"""
        if not rule.source_field or rule.source_field not in data:
            return {}
            
        target_type = (rule.parameters or {}).get("target_type")
        if not target_type:
            return {}

        try:
            converted_value = self._convert_data_type(data[rule.source_field], target_type)
            data[rule.source_field] = converted_value
        except Exception as e:
            return {"warning": f"Type conversion failed for field {rule.source_field}: {str(e)}"}
        
        return {}

    def _apply_normalization_rule(
        self, 
        data: Dict[str, Any], 
        rule: TransformationRule
    ) -> Dict[str, Any]:
        """Apply value normalization transformation"""
        if not rule.source_field or rule.source_field not in data:
            return {}
            
        normalization_type = (rule.parameters or {}).get("normalization_type", "lowercase")
        value = data[rule.source_field]
        
        try:
            if normalization_type == "lowercase" and isinstance(value, str):
                data[rule.source_field] = value.lower()
            elif normalization_type == "uppercase" and isinstance(value, str):
                data[rule.source_field] = value.upper()
            elif normalization_type == "trim" and isinstance(value, str):
                data[rule.source_field] = value.strip()
            elif normalization_type == "remove_spaces" and isinstance(value, str):
                data[rule.source_field] = re.sub(r'\s+', '', value)
            elif normalization_type == "normalize_phone" and isinstance(value, str):
                data[rule.source_field] = self._normalize_phone_number(value)
            elif normalization_type == "normalize_email" and isinstance(value, str):
                data[rule.source_field] = value.lower().strip()
        except Exception as e:
            return {"warning": f"Normalization failed for field {rule.source_field}: {str(e)}"}
        
        return {}

    def _apply_business_logic_rule(
        self, 
        data: Dict[str, Any], 
        rule: TransformationRule
    ) -> Dict[str, Any]:
        """Apply business logic transformation"""
        if rule.rule_function:
            try:
                result = rule.rule_function(data, rule.parameters)
                if isinstance(result, dict):
                    data.update(result)
            except Exception as e:
                return {"warning": f"Business logic rule {rule.name} failed: {str(e)}"}
        return {}

    def _apply_aggregation_rule(
        self, 
        data: Dict[str, Any], 
        rule: TransformationRule
    ) -> Dict[str, Any]:
        """Apply aggregation transformation"""
        aggregation_type = (rule.parameters or {}).get("aggregation_type", "sum")
        source_fields = (rule.parameters or {}).get("source_fields", [])
        target_field = rule.target_field or "aggregated_value"
        
        try:
            values = [data.get(field, 0) for field in source_fields if field in data]
            
            if aggregation_type == "sum":
                data[target_field] = sum(values)
            elif aggregation_type == "average":
                data[target_field] = sum(values) / len(values) if values else 0
            elif aggregation_type == "max":
                data[target_field] = max(values) if values else 0
            elif aggregation_type == "min":
                data[target_field] = min(values) if values else 0
            elif aggregation_type == "count":
                data[target_field] = len(values)
        except Exception as e:
            return {"warning": f"Aggregation failed: {str(e)}"}
        
        return {}

    def _apply_field_mappings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default field mappings"""
        for source_field, target_field in self.field_mappings.items():
            if source_field in data and target_field != source_field:
                data[target_field] = data[source_field]
                del data[source_field]
        return data

    def _apply_type_conversions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default type conversions"""
        for field, target_type in self.type_conversions.items():
            if field in data:
                try:
                    data[field] = self._convert_data_type(data[field], target_type)
                except Exception as e:
                    logger.warning(f"Type conversion failed for field {field}: {str(e)}")
        return data

    def _convert_data_type(self, value: Any, target_type: DataType) -> Any:
        """Convert value to target data type"""
        if target_type == DataType.STRING:
            return str(value)
        elif target_type == DataType.INTEGER:
            return int(float(value))
        elif target_type == DataType.FLOAT:
            return float(value)
        elif target_type == DataType.DECIMAL:
            return Decimal(str(value))
        elif target_type == DataType.BOOLEAN:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif target_type == DataType.DATE:
            if isinstance(value, str):
                return datetime.strptime(value, "%Y-%m-%d").date()
            return value
        elif target_type == DataType.DATETIME:
            if isinstance(value, str):
                return datetime.fromisoformat(value)
            return value
        else:
            return value

    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Format as standard US phone number if 10 digits
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't normalize

    def transform_batch_data(
        self, 
        data_list: List[Dict[str, Any]],
        rules: Optional[List[TransformationRule]] = None
    ) -> List[TransformationResult]:
        """Transform a batch of data records"""
        results = []
        for data in data_list:
            result = self.transform_data(data, rules)
            results.append(result)
        return results

    def create_agent_billing_transformation(self) -> List[TransformationRule]:
        """Create transformation rules specific to agent billing data"""
        return [
            TransformationRule(
                name="normalize_agent_name",
                transformation_type=TransformationType.VALUE_NORMALIZATION,
                source_field="agent_name",
                parameters={"normalization_type": "trim"},
                priority=100,
                description="Normalize agent name by trimming whitespace"
            ),
            TransformationRule(
                name="convert_cost_to_decimal",
                transformation_type=TransformationType.TYPE_CONVERSION,
                source_field="cost",
                parameters={"target_type": DataType.DECIMAL},
                priority=90,
                description="Convert cost values to decimal type"
            ),
            TransformationRule(
                name="calculate_total_cost",
                transformation_type=TransformationType.BUSINESS_LOGIC,
                rule_function=lambda data, params: {
                    "total_cost": data.get("base_cost", 0) + data.get("additional_cost", 0)
                },
                priority=80,
                description="Calculate total cost from base and additional costs"
            )
        ]

    def create_integration_data_transformation(self) -> List[TransformationRule]:
        """Create transformation rules for integration data"""
        return [
            TransformationRule(
                name="map_external_id",
                transformation_type=TransformationType.FIELD_MAPPING,
                source_field="external_agent_id",
                target_field="agent_external_id",
                priority=100,
                description="Map external agent ID field"
            ),
            TransformationRule(
                name="normalize_timestamps",
                transformation_type=TransformationType.TYPE_CONVERSION,
                source_field="timestamp",
                parameters={"target_type": DataType.DATETIME},
                priority=90,
                description="Convert timestamp to datetime format"
            )
        ]


# Utility functions for common transformations
def create_currency_transformation_rule(field_name: str, target_currency: str = "USD") -> TransformationRule:
    """Create a transformation rule for currency conversion"""
    def currency_converter(data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        # This would integrate with a currency conversion service
        # For now, just ensure proper formatting
        value = data.get(field_name, 0)
        if isinstance(value, (int, float)):
            data[field_name] = f"{value:.2f}"
        return {}
    
    return TransformationRule(
        name=f"convert_{field_name}_currency",
        transformation_type=TransformationType.BUSINESS_LOGIC,
        rule_function=currency_converter,
        parameters={"target_currency": target_currency},
        description=f"Convert {field_name} to {target_currency} format"
    )


def create_email_normalization_rule(field_name: str) -> TransformationRule:
    """Create a transformation rule for email normalization"""
    return TransformationRule(
        name=f"normalize_{field_name}_email",
        transformation_type=TransformationType.VALUE_NORMALIZATION,
        source_field=field_name,
        parameters={"normalization_type": "normalize_email"},
        description=f"Normalize email format for {field_name}"
    )
