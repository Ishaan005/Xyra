"""
Data Enrichment Service for Xyra Platform

Provides comprehensive data enrichment capabilities including:
- External data source integration
- Data augmentation and enhancement
- Contextual information addition
- Machine learning-based enrichment
- Real-time and batch enrichment processing

Designed for the AI agent monetization platform to enhance data quality
and provide additional context for billing, analytics, and reporting.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import asyncio
import aiohttp
import json
from enum import Enum
from dataclasses import dataclass, field
import logging
from abc import ABC, abstractmethod
from app.utils.validation import DataValidator, ValidationResult
from app.services.data_transformation import DataTransformationService, TransformationResult

logger = logging.getLogger(__name__)


class EnrichmentType(str, Enum):
    """Types of data enrichment"""
    EXTERNAL_API = "external_api"
    DATABASE_LOOKUP = "database_lookup"
    CALCULATION = "calculation"
    GEO_LOCATION = "geo_location"
    ML_PREDICTION = "ml_prediction"
    CONTEXTUAL = "contextual"
    AUDIT = "audit"


class EnrichmentPriority(str, Enum):
    """Priority levels for enrichment operations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EnrichmentStatus(str, Enum):
    """Status of enrichment operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class EnrichmentRule:
    """Defines a single enrichment rule"""
    name: str
    enrichment_type: EnrichmentType
    source_fields: List[str]
    target_fields: List[str]
    enrichment_function: Optional[Callable] = None
    external_source: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Callable] = None
    priority: EnrichmentPriority = EnrichmentPriority.MEDIUM
    cache_ttl: Optional[int] = None  # TTL in seconds
    async_processing: bool = False
    retry_count: int = 3
    timeout: int = 30
    description: str = ""


@dataclass
class EnrichmentResult:
    """Result of an enrichment operation"""
    success: bool
    status: EnrichmentStatus
    message: str
    enriched_data: Optional[Dict[str, Any]] = None
    original_data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: Optional[float] = None
    cache_hit: bool = False


class EnrichmentProvider(ABC):
    """Abstract base class for enrichment providers"""
    
    @abstractmethod
    async def enrich(
        self, 
        data: Dict[str, Any], 
        rule: EnrichmentRule
    ) -> EnrichmentResult:
        """Perform enrichment on the provided data"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate provider configuration"""
        pass


class GeolocationProvider(EnrichmentProvider):
    """Provider for geolocation enrichment"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.ipgeolocation.io"):
        self.api_key = api_key
        self.base_url = base_url
    
    async def enrich(
        self, 
        data: Dict[str, Any], 
        rule: EnrichmentRule
    ) -> EnrichmentResult:
        """Enrich data with geolocation information"""
        start_time = datetime.now()
        
        try:
            ip_address = None
            for field in rule.source_fields:
                if field in data and data[field]:
                    ip_address = data[field]
                    break
            
            if not ip_address:
                return EnrichmentResult(
                    success=False,
                    status=EnrichmentStatus.SKIPPED,
                    message="No IP address found in source fields",
                    original_data=data
                )
            
            # Make API call to get geolocation data
            geo_data = await self._get_geolocation_data(ip_address)
            
            if geo_data:
                enriched_data = data.copy()
                for i, target_field in enumerate(rule.target_fields):
                    if i == 0:
                        enriched_data[target_field] = geo_data.get("country_name")
                    elif i == 1:
                        enriched_data[target_field] = geo_data.get("city")
                    elif i == 2:
                        enriched_data[target_field] = geo_data.get("latitude")
                    elif i == 3:
                        enriched_data[target_field] = geo_data.get("longitude")
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return EnrichmentResult(
                    success=True,
                    status=EnrichmentStatus.COMPLETED,
                    message="Geolocation enrichment completed successfully",
                    enriched_data=enriched_data,
                    original_data=data,
                    processing_time=processing_time,
                    metadata={"geo_data": geo_data}
                )
            else:
                return EnrichmentResult(
                    success=False,
                    status=EnrichmentStatus.FAILED,
                    message="Failed to retrieve geolocation data",
                    original_data=data
                )
                
        except Exception as e:
            logger.error(f"Geolocation enrichment failed: {str(e)}")
            return EnrichmentResult(
                success=False,
                status=EnrichmentStatus.FAILED,
                message=f"Geolocation enrichment error: {str(e)}",
                original_data=data,
                errors=[str(e)]
            )
    
    async def _get_geolocation_data(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get geolocation data from external API"""
        try:
            url = f"{self.base_url}/ipgeo"
            params = {"apiKey": self.api_key, "ip": ip_address}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Geolocation API returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to fetch geolocation data: {str(e)}")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate geolocation provider configuration"""
        return "api_key" in config or self.api_key is not None


class DatabaseLookupProvider(EnrichmentProvider):
    """Provider for database lookup enrichment"""
    
    def __init__(self, db_session_factory: Callable):
        self.db_session_factory = db_session_factory
    
    async def enrich(
        self, 
        data: Dict[str, Any], 
        rule: EnrichmentRule
    ) -> EnrichmentResult:
        """Enrich data with database lookup"""
        start_time = datetime.now()
        
        try:
            lookup_value = None
            lookup_field = None
            
            for field in rule.source_fields:
                if field in data and data[field]:
                    lookup_value = data[field]
                    lookup_field = field
                    break
            
            if not lookup_value or not lookup_field:
                return EnrichmentResult(
                    success=False,
                    status=EnrichmentStatus.SKIPPED,
                    message="No lookup value found in source fields",
                    original_data=data
                )
            
            # Perform database lookup
            lookup_data = await self._perform_database_lookup(
                lookup_field, 
                lookup_value, 
                rule.parameters
            )
            
            if lookup_data:
                enriched_data = data.copy()
                
                # Map lookup results to target fields
                for i, target_field in enumerate(rule.target_fields):
                    if i < len(lookup_data):
                        enriched_data[target_field] = lookup_data[i]
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return EnrichmentResult(
                    success=True,
                    status=EnrichmentStatus.COMPLETED,
                    message="Database lookup enrichment completed successfully",
                    enriched_data=enriched_data,
                    original_data=data,
                    processing_time=processing_time,
                    metadata={"lookup_data": lookup_data}
                )
            else:
                return EnrichmentResult(
                    success=False,
                    status=EnrichmentStatus.COMPLETED,
                    message="No data found in database lookup",
                    enriched_data=data,
                    original_data=data,
                    warnings=["Database lookup returned no results"]
                )
                
        except Exception as e:
            logger.error(f"Database lookup enrichment failed: {str(e)}")
            return EnrichmentResult(
                success=False,
                status=EnrichmentStatus.FAILED,
                message=f"Database lookup error: {str(e)}",
                original_data=data,
                errors=[str(e)]
            )
    
    async def _perform_database_lookup(
        self, 
        lookup_field: str, 
        lookup_value: Any, 
        parameters: Dict[str, Any]
    ) -> Optional[List[Any]]:
        """Perform the actual database lookup"""
        try:
            table_name = parameters.get("table")
            lookup_column = parameters.get("lookup_column", lookup_field)
            return_columns = parameters.get("return_columns", [])
            
            if not table_name or not return_columns:
                return None
            
            # This would be implemented with actual database queries
            # For now, return placeholder data
            return ["enriched_value_1", "enriched_value_2"]
            
        except Exception as e:
            logger.error(f"Database lookup failed: {str(e)}")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate database lookup provider configuration"""
        required_fields = ["table", "lookup_column", "return_columns"]
        return all(field in config for field in required_fields)


class CalculationProvider(EnrichmentProvider):
    """Provider for calculation-based enrichment"""
    
    async def enrich(
        self, 
        data: Dict[str, Any], 
        rule: EnrichmentRule
    ) -> EnrichmentResult:
        """Enrich data with calculated values"""
        start_time = datetime.now()
        
        try:
            enriched_data = data.copy()
            calculation_type = rule.parameters.get("calculation_type", "sum")
            
            # Get source values
            source_values = []
            for field in rule.source_fields:
                if field in data:
                    try:
                        value = float(data[field]) if data[field] is not None else 0
                        source_values.append(value)
                    except (ValueError, TypeError):
                        source_values.append(0)
            
            # Perform calculation
            if calculation_type == "sum":
                result = sum(source_values)
            elif calculation_type == "average":
                result = sum(source_values) / len(source_values) if source_values else 0
            elif calculation_type == "max":
                result = max(source_values) if source_values else 0
            elif calculation_type == "min":
                result = min(source_values) if source_values else 0
            elif calculation_type == "product":
                result = 1
                for value in source_values:
                    result *= value
            elif calculation_type == "percentage":
                base_value = rule.parameters.get("base_value", 1)
                result = (sum(source_values) / base_value) * 100 if base_value != 0 else 0
            else:
                result = 0
            
            # Apply result to target fields
            for target_field in rule.target_fields:
                enriched_data[target_field] = result
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EnrichmentResult(
                success=True,
                status=EnrichmentStatus.COMPLETED,
                message="Calculation enrichment completed successfully",
                enriched_data=enriched_data,
                original_data=data,
                processing_time=processing_time,
                metadata={
                    "calculation_type": calculation_type,
                    "source_values": source_values,
                    "result": result
                }
            )
            
        except Exception as e:
            logger.error(f"Calculation enrichment failed: {str(e)}")
            return EnrichmentResult(
                success=False,
                status=EnrichmentStatus.FAILED,
                message=f"Calculation error: {str(e)}",
                original_data=data,
                errors=[str(e)]
            )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate calculation provider configuration"""
        return "calculation_type" in config


class AuditProvider(EnrichmentProvider):
    """Provider for audit trail enrichment"""
    
    async def enrich(
        self, 
        data: Dict[str, Any], 
        rule: EnrichmentRule
    ) -> EnrichmentResult:
        """Enrich data with audit information"""
        start_time = datetime.now()
        
        try:
            enriched_data = data.copy()
            
            # Add audit fields
            current_time = datetime.now()
            audit_fields = {
                "enriched_at": current_time.isoformat(),
                "enriched_by": "data_enrichment_service",
                "enrichment_version": "1.0",
                "data_quality_score": self._calculate_data_quality_score(data)
            }
            
            # Apply audit fields to target fields
            for i, target_field in enumerate(rule.target_fields):
                if i == 0:
                    enriched_data[target_field] = audit_fields["enriched_at"]
                elif i == 1:
                    enriched_data[target_field] = audit_fields["enriched_by"]
                elif i == 2:
                    enriched_data[target_field] = audit_fields["enrichment_version"]
                elif i == 3:
                    enriched_data[target_field] = audit_fields["data_quality_score"]
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EnrichmentResult(
                success=True,
                status=EnrichmentStatus.COMPLETED,
                message="Audit enrichment completed successfully",
                enriched_data=enriched_data,
                original_data=data,
                processing_time=processing_time,
                metadata=audit_fields
            )
            
        except Exception as e:
            logger.error(f"Audit enrichment failed: {str(e)}")
            return EnrichmentResult(
                success=False,
                status=EnrichmentStatus.FAILED,
                message=f"Audit enrichment error: {str(e)}",
                original_data=data,
                errors=[str(e)]
            )
    
    def _calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate a data quality score based on completeness and validity"""
        total_fields = len(data)
        if total_fields == 0:
            return 0.0
        
        complete_fields = sum(1 for value in data.values() if value is not None and value != "")
        return (complete_fields / total_fields) * 100
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate audit provider configuration"""
        return True  # Audit provider doesn't require specific configuration


class DataEnrichmentService:
    """
    Core data enrichment service for the Xyra platform.
    Provides comprehensive enrichment capabilities with multiple providers
    and integration with validation and transformation services.
    """
    
    def __init__(
        self, 
        validation_framework: Optional[DataValidator] = None,
        transformation_service: Optional[DataTransformationService] = None
    ):
        self.validation_framework = validation_framework or DataValidator()
        self.transformation_service = transformation_service or DataTransformationService()
        self.enrichment_rules: List[EnrichmentRule] = []
        self.providers: Dict[EnrichmentType, EnrichmentProvider] = {}
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # Initialize default providers
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Initialize default enrichment providers"""
        self.providers[EnrichmentType.CALCULATION] = CalculationProvider()
        self.providers[EnrichmentType.AUDIT] = AuditProvider()
        # Other providers would be initialized with proper configuration
    
    def add_provider(self, enrichment_type: EnrichmentType, provider: EnrichmentProvider):
        """Add an enrichment provider"""
        self.providers[enrichment_type] = provider
    
    def add_enrichment_rule(self, rule: EnrichmentRule):
        """Add an enrichment rule"""
        self.enrichment_rules.append(rule)
        # Sort by priority (CRITICAL first)
        priority_order = {
            EnrichmentPriority.CRITICAL: 4,
            EnrichmentPriority.HIGH: 3,
            EnrichmentPriority.MEDIUM: 2,
            EnrichmentPriority.LOW: 1
        }
        self.enrichment_rules.sort(key=lambda x: priority_order.get(x.priority, 0), reverse=True)
    
    async def enrich_data(
        self, 
        data: Dict[str, Any],
        rules: Optional[List[EnrichmentRule]] = None,
        validate_input: bool = True,
        transform_after_enrichment: bool = False
    ) -> EnrichmentResult:
        """
        Enrich data using specified rules or default rules
        
        Args:
            data: Input data to enrich
            rules: Optional specific rules to apply
            validate_input: Whether to validate input data
            transform_after_enrichment: Whether to apply transformations after enrichment
            
        Returns:
            EnrichmentResult with enriched data and metadata
        """
        try:
            # Input validation
            if validate_input:
                validation_result = self.validation_framework.validate(data, "default")
                if not validation_result.is_valid:
                    return EnrichmentResult(
                        success=False,
                        status=EnrichmentStatus.FAILED,
                        message="Input validation failed",
                        original_data=data,
                        errors=[f"Validation error: {error.message}" for error in validation_result.errors]
                    )
            
            # Apply enrichment rules
            rules_to_apply = rules or self.enrichment_rules
            enriched_data = data.copy()
            errors = []
            warnings = []
            metadata = {
                "rules_applied": [],
                "enrichments_count": 0,
                "processing_time": None,
                "cache_hits": 0
            }
            
            start_time = datetime.now()
            
            for rule in rules_to_apply:
                try:
                    # Check condition if specified
                    if rule.condition and not rule.condition(enriched_data):
                        continue
                    
                    # Check cache if TTL specified
                    cache_key = self._generate_cache_key(enriched_data, rule)
                    cached_result = self._get_cached_result(cache_key, rule.cache_ttl)
                    
                    if cached_result:
                        enriched_data.update(cached_result)
                        metadata["cache_hits"] += 1
                        metadata["rules_applied"].append(f"{rule.name} (cached)")
                        continue
                    
                    # Apply enrichment rule
                    provider = self.providers.get(rule.enrichment_type)
                    if not provider:
                        warnings.append(f"No provider found for enrichment type: {rule.enrichment_type}")
                        continue
                    
                    if rule.async_processing:
                        result = await provider.enrich(enriched_data, rule)
                    else:
                        result = await provider.enrich(enriched_data, rule)
                    
                    if result.success and result.enriched_data:
                        # Cache the result if TTL specified
                        if rule.cache_ttl:
                            enrichment_diff = {
                                k: v for k, v in result.enriched_data.items() 
                                if k not in enriched_data or enriched_data[k] != v
                            }
                            self._cache_result(cache_key, enrichment_diff, rule.cache_ttl)
                        
                        enriched_data = result.enriched_data
                        metadata["rules_applied"].append(rule.name)
                        metadata["enrichments_count"] += 1
                        
                        if result.warnings:
                            warnings.extend(result.warnings)
                    else:
                        if result.errors:
                            errors.extend(result.errors)
                        warnings.append(f"Enrichment rule {rule.name} failed: {result.message}")
                        
                except Exception as e:
                    logger.error(f"Error applying enrichment rule {rule.name}: {str(e)}")
                    errors.append(f"Failed to apply enrichment rule {rule.name}: {str(e)}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            metadata["processing_time"] = processing_time
            
            # Apply transformations if requested
            if transform_after_enrichment:
                transformation_result = self.transformation_service.transform_data(
                    enriched_data, 
                    validate_input=False
                )
                if transformation_result.success and transformation_result.transformed_data:
                    enriched_data = transformation_result.transformed_data
                    metadata["transformation_applied"] = True
                    if transformation_result.warnings:
                        warnings.extend(transformation_result.warnings)
            
            return EnrichmentResult(
                success=len(errors) == 0,
                status=EnrichmentStatus.COMPLETED if len(errors) == 0 else EnrichmentStatus.FAILED,
                message="Data enrichment completed" + (" with warnings" if warnings else " successfully"),
                enriched_data=enriched_data,
                original_data=data,
                errors=errors,
                warnings=warnings,
                metadata=metadata,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Data enrichment failed: {str(e)}")
            return EnrichmentResult(
                success=False,
                status=EnrichmentStatus.FAILED,
                message="Data enrichment failed",
                original_data=data,
                errors=[str(e)]
            )
    
    def _generate_cache_key(self, data: Dict[str, Any], rule: EnrichmentRule) -> str:
        """Generate cache key for enrichment result"""
        source_values = [str(data.get(field, "")) for field in rule.source_fields]
        return f"{rule.name}:{':'.join(source_values)}"
    
    def _get_cached_result(self, cache_key: str, ttl: Optional[int]) -> Optional[Dict[str, Any]]:
        """Get cached enrichment result if still valid"""
        if not ttl or cache_key not in self.cache:
            return None
        
        cached_data, cached_time = self.cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() > ttl:
            del self.cache[cache_key]
            return None
        
        return cached_data
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int):
        """Cache enrichment result"""
        self.cache[cache_key] = (result, datetime.now())
    
    async def enrich_batch_data(
        self, 
        data_list: List[Dict[str, Any]],
        rules: Optional[List[EnrichmentRule]] = None,
        max_concurrent: int = 10
    ) -> List[EnrichmentResult]:
        """Enrich a batch of data records with concurrency control"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def enrich_single(data: Dict[str, Any]) -> EnrichmentResult:
            async with semaphore:
                return await self.enrich_data(data, rules)
        
        tasks = [enrich_single(data) for data in data_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        enrichment_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                enrichment_results.append(EnrichmentResult(
                    success=False,
                    status=EnrichmentStatus.FAILED,
                    message=f"Batch enrichment failed: {str(result)}",
                    original_data=data_list[i] if i < len(data_list) else {},
                    errors=[str(result)]
                ))
            else:
                enrichment_results.append(result)
        
        return enrichment_results
    
    def create_agent_billing_enrichment_rules(self) -> List[EnrichmentRule]:
        """Create enrichment rules specific to agent billing data"""
        return [
            EnrichmentRule(
                name="calculate_usage_metrics",
                enrichment_type=EnrichmentType.CALCULATION,
                source_fields=["requests_count", "processing_time"],
                target_fields=["average_response_time"],
                parameters={
                    "calculation_type": "average"
                },
                priority=EnrichmentPriority.HIGH,
                description="Calculate average response time from usage data"
            ),
            EnrichmentRule(
                name="add_billing_audit_trail",
                enrichment_type=EnrichmentType.AUDIT,
                source_fields=["agent_id", "cost"],
                target_fields=["audit_timestamp", "audit_user", "audit_version", "data_quality_score"],
                priority=EnrichmentPriority.MEDIUM,
                description="Add audit trail for billing records"
            )
        ]
    
    def create_geolocation_enrichment_rules(self, api_key: str) -> List[EnrichmentRule]:
        """Create enrichment rules for geolocation data"""
        # Add geolocation provider if not already added
        if EnrichmentType.GEO_LOCATION not in self.providers:
            self.providers[EnrichmentType.GEO_LOCATION] = GeolocationProvider(api_key)
        
        return [
            EnrichmentRule(
                name="enrich_user_location",
                enrichment_type=EnrichmentType.GEO_LOCATION,
                source_fields=["ip_address"],
                target_fields=["country", "city", "latitude", "longitude"],
                priority=EnrichmentPriority.MEDIUM,
                cache_ttl=3600,  # Cache for 1 hour
                description="Enrich user data with geolocation information"
            )
        ]


# Utility functions for common enrichment patterns
def create_timestamp_enrichment_rule() -> EnrichmentRule:
    """Create a rule to add current timestamp"""
    return EnrichmentRule(
        name="add_current_timestamp",
        enrichment_type=EnrichmentType.CALCULATION,
        source_fields=[],
        target_fields=["enriched_timestamp"],
        parameters={
            "calculation_type": "current_time"
        },
        description="Add current timestamp to data"
    )


def create_data_quality_enrichment_rule() -> EnrichmentRule:
    """Create a rule to calculate data quality score"""
    return EnrichmentRule(
        name="calculate_data_quality",
        enrichment_type=EnrichmentType.AUDIT,
        source_fields=["*"],  # All fields
        target_fields=["data_quality_score"],
        description="Calculate data quality score based on completeness"
    )
