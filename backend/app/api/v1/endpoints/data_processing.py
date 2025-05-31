"""
Data Processing API Endpoints for Xyra Platform

Provides comprehensive data processing capabilities including:
- Data validation endpoints
- Data transformation endpoints  
- Data enrichment endpoints
- Pipeline orchestration endpoints
- Data quality metrics endpoints
"""

from typing import Any, List, Optional, Dict, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.api.data_processing_deps import (
    get_data_processing_pipeline,
    get_data_validator,
    get_transformation_service,
    get_enrichment_service
)
from app.services.data_processing_pipeline import (
    DataProcessingPipeline, 
    ProcessingStage, 
    PipelineMode,
    PipelineConfig,
    ProcessingStrategy
)
from app.services.data_transformation import (
    DataTransformationService,
    TransformationRule,
    TransformationType
)
from app.services.data_enrichment import (
    DataEnrichmentService,
    EnrichmentRule,
    EnrichmentType,
    EnrichmentPriority
)
from app.utils.validation import DataValidator, ValidationRule
import pandas as pd
import json

router = APIRouter()


# Validation Endpoints
@router.post("/validate", response_model=Dict[str, Any])
def validate_data(
    *,
    data: Dict[str, Any] = Body(..., description="Data to validate"),
    validation_type: str = Query("default", description="Type of validation to perform"),
    validator: DataValidator = Depends(get_data_validator),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Validate data using the data validation framework.
    """
    try:
        validation_result = validator.validate(data, validation_type)
        return {
            "is_valid": validation_result.is_valid,
            "errors": [{"field": err.field, "message": err.message, "severity": err.severity} for err in validation_result.errors],
            "warnings": [{"field": warn.field, "message": warn.message} for warn in validation_result.warnings],
            "validation_type": validation_type,
            "data_processed": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/validation-rules", response_model=List[Dict[str, Any]])
def get_validation_rules(
    *,
    validation_type: Optional[str] = Query(None, description="Filter by validation type"),
    validator: DataValidator = Depends(get_data_validator),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get available validation rules.
    """
    try:
        if validation_type:
            rules = validator.get_rules_by_type(validation_type)
        else:
            rules = validator.get_all_rules()
        
        return [
            {
                "rule_name": rule.get("rule_name", ""),
                "field": rule.get("field", ""),
                "validation_type": rule.get("validation_type", ""),
                "required": rule.get("required", False),
                "description": rule.get("description", "")
            }
            for rule in rules
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve validation rules: {str(e)}"
        )


# Transformation Endpoints
@router.post("/transform", response_model=Dict[str, Any])
async def transform_data(
    *,
    data: Dict[str, Any] = Body(..., description="Data to transform"),
    transformation_rules: List[Dict[str, Any]] = Body(..., description="Transformation rules to apply"),
    transformation_service: DataTransformationService = Depends(get_transformation_service),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Transform data using specified transformation rules.
    """
    try:
        # Convert rule dictionaries to TransformationRule objects
        rules = []
        for rule_dict in transformation_rules:
            rule = TransformationRule(
                name=rule_dict.get("name", ""),
                transformation_type=TransformationType(rule_dict.get("transformation_type", "VALUE_NORMALIZATION")),
                source_field=rule_dict.get("source_field"),
                target_field=rule_dict.get("target_field"),
                parameters=rule_dict.get("parameters", {}),
                description=rule_dict.get("description", "")
            )
            rules.append(rule)
        
        # Apply transformations
        transformation_result = transformation_service.transform_data(data, rules)
        
        return {
            "success": transformation_result.success,
            "transformed_data": transformation_result.transformed_data,
            "errors": transformation_result.errors,
            "warnings": transformation_result.warnings,
            "metadata": transformation_result.metadata
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transformation failed: {str(e)}"
        )


@router.get("/transformation-types", response_model=List[str])
def get_transformation_types(
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get available transformation types.
    """
    return [t.value for t in TransformationType]


# Enrichment Endpoints
@router.post("/enrich", response_model=Dict[str, Any])
async def enrich_data(
    *,
    data: Dict[str, Any] = Body(..., description="Data to enrich"),
    enrichment_rules: List[Dict[str, Any]] = Body(..., description="Enrichment rules to apply"),
    validate_input: bool = Query(True, description="Whether to validate input data"),
    enrichment_service: DataEnrichmentService = Depends(get_enrichment_service),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Enrich data using specified enrichment rules.
    """
    try:
        # Convert rule dictionaries to EnrichmentRule objects
        rules = []
        for rule_dict in enrichment_rules:
            rule = EnrichmentRule(
                name=rule_dict.get("name", ""),
                enrichment_type=EnrichmentType(rule_dict.get("enrichment_type", "CONTEXTUAL")),
                source_fields=rule_dict.get("source_fields", []),
                target_fields=rule_dict.get("target_fields", []),
                parameters=rule_dict.get("parameters", {}),
                priority=EnrichmentPriority(rule_dict.get("priority", "MEDIUM")),
                description=rule_dict.get("description", "")
            )
            rules.append(rule)
        
        # Apply enrichment
        enrichment_result = await enrichment_service.enrich_data(data, rules, validate_input)
        
        return {
            "success": enrichment_result.success,
            "status": enrichment_result.status,
            "enriched_data": enrichment_result.enriched_data,
            "original_data": enrichment_result.original_data,
            "errors": enrichment_result.errors,
            "warnings": enrichment_result.warnings,
            "metadata": enrichment_result.metadata,
            "processing_time": enrichment_result.processing_time,
            "cache_hit": enrichment_result.cache_hit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Enrichment failed: {str(e)}"
        )


@router.get("/enrichment-types", response_model=List[str])
def get_enrichment_types(
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get available enrichment types.
    """
    return [t.value for t in EnrichmentType]


# Pipeline Orchestration Endpoints
@router.post("/pipeline/process", response_model=Dict[str, Any])
async def process_data_pipeline(
    *,
    data: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(..., description="Data to process"),
    transformation_rules: Optional[List[Dict[str, Any]]] = Body(None, description="Transformation rules"),
    enrichment_rules: Optional[List[Dict[str, Any]]] = Body(None, description="Enrichment rules"),
    pipeline_config: Optional[Dict[str, Any]] = Body(None, description="Custom pipeline configuration"),
    pipeline: DataProcessingPipeline = Depends(get_data_processing_pipeline),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Process data through the complete data processing pipeline.
    """
    try:
        # Convert rule dictionaries to objects if provided
        transformation_rule_objects = None
        if transformation_rules:
            transformation_rule_objects = [
                TransformationRule(
                    name=rule.get("name", ""),
                    transformation_type=TransformationType(rule.get("transformation_type", "VALUE_MAPPING")),
                    source_field=rule.get("source_field", ""),
                    target_field=rule.get("target_field", ""),
                    parameters=rule.get("parameters", {}),
                    description=rule.get("description", "")
                )
                for rule in transformation_rules
            ]
        
        enrichment_rule_objects = None
        if enrichment_rules:
            enrichment_rule_objects = [
                EnrichmentRule(
                    name=rule.get("name", ""),
                    enrichment_type=EnrichmentType(rule.get("enrichment_type", "CONTEXTUAL")),
                    source_fields=rule.get("source_fields", []),
                    target_fields=rule.get("target_fields", []),
                    parameters=rule.get("parameters", {}),
                    priority=EnrichmentPriority(rule.get("priority", "MEDIUM")),
                    description=rule.get("description", "")
                )
                for rule in enrichment_rules
            ]
        
        # Create custom config if provided
        custom_config = None
        if pipeline_config:
            custom_config = PipelineConfig(
                name=pipeline_config.get("name", "custom_pipeline"),
                processing_mode=PipelineMode(pipeline_config.get("processing_mode", "BATCH")),
                enabled_stages=[ProcessingStage(stage) for stage in pipeline_config.get("enabled_stages", ["validation", "transformation", "enrichment"])],
                max_concurrent=pipeline_config.get("max_concurrent", 4),
                error_strategy=ProcessingStrategy(pipeline_config.get("error_strategy", "continue_on_error")),
                batch_size=pipeline_config.get("batch_size", 100),
                max_retries=pipeline_config.get("max_retries", 3),
                enable_caching=pipeline_config.get("enable_caching", True),
                enable_monitoring=pipeline_config.get("enable_monitoring", True)
            )
        
        # Process data through pipeline
        processing_result = await pipeline.process_data(
            data=data,
            transformation_rules=transformation_rule_objects,
            enrichment_rules=enrichment_rule_objects,
            custom_config=custom_config
        )
        
        return {
            "success": processing_result.success,
            "processed_data": processing_result.output_data,
            "metadata": processing_result.metadata,
            "errors": processing_result.errors,
            "warnings": processing_result.warnings,
            "total_records": processing_result.total_records,
            "processed_records": processing_result.processed_records,
            "failed_records": processing_result.failed_records,
            "stage_results": processing_result.stage_results,
            "processing_time": processing_result.processing_time
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline processing failed: {str(e)}"
        )


@router.get("/pipeline/config", response_model=Dict[str, Any])
def get_pipeline_config(
    pipeline: DataProcessingPipeline = Depends(get_data_processing_pipeline),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current pipeline configuration.
    """
    try:
        config = pipeline.config
        return {
            "name": config.name,
            "processing_mode": config.processing_mode,
            "enabled_stages": config.enabled_stages,
            "error_strategy": config.error_strategy,
            "max_concurrent": config.max_concurrent,
            "batch_size": config.batch_size,
            "max_retries": config.max_retries,
            "enable_caching": config.enable_caching,
            "enable_monitoring": config.enable_monitoring,
            "processing_stats": pipeline.processing_stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pipeline configuration: {str(e)}"
        )


# Data Quality and Metrics Endpoints
@router.get("/metrics/pipeline", response_model=Dict[str, Any])
def get_pipeline_metrics(
    pipeline: DataProcessingPipeline = Depends(get_data_processing_pipeline),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get pipeline performance and data quality metrics.
    """
    try:
        return {
            "processing_stats": pipeline.processing_stats,
            "total_processed": pipeline.processing_stats.get("total_processed", 0),
            "total_errors": pipeline.processing_stats.get("total_errors", 0),
            "error_rate": pipeline.processing_stats.get("total_errors", 0) / max(pipeline.processing_stats.get("total_processed", 1), 1),
            "stage_performance": pipeline.processing_stats.get("stage_performance", {}),
            "success_rate": 1 - (pipeline.processing_stats.get("total_errors", 0) / max(pipeline.processing_stats.get("total_processed", 1), 1))
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pipeline metrics: {str(e)}"
        )


@router.post("/metrics/data-quality", response_model=Dict[str, Any])
def analyze_data_quality(
    *,
    data: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(..., description="Data to analyze"),
    validator: DataValidator = Depends(get_data_validator),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Analyze data quality metrics.
    """
    try:
        if isinstance(data, dict):
            data = [data]
        
        total_records = len(data)
        valid_records = 0
        total_errors = 0
        total_warnings = 0
        field_completeness = {}
        
        for record in data:
            validation_result = validator.validate(record, "default")
            if validation_result.is_valid:
                valid_records += 1
            total_errors += len(validation_result.errors)
            total_warnings += len(validation_result.warnings)
            
            # Analyze field completeness
            for field, value in record.items():
                if field not in field_completeness:
                    field_completeness[field] = {"total": 0, "filled": 0}
                field_completeness[field]["total"] += 1
                if value is not None and value != "":
                    field_completeness[field]["filled"] += 1
        
        # Calculate completeness percentages
        completeness_percentages = {}
        for field, stats in field_completeness.items():
            completeness_percentages[field] = (stats["filled"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        
        return {
            "total_records": total_records,
            "valid_records": valid_records,
            "validity_rate": (valid_records / total_records) * 100 if total_records > 0 else 0,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "error_rate": (total_errors / total_records) if total_records > 0 else 0,
            "field_completeness": completeness_percentages,
            "overall_completeness": sum(completeness_percentages.values()) / len(completeness_percentages) if completeness_percentages else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data quality analysis failed: {str(e)}"
        )


# Health Check Endpoints
@router.get("/health", response_model=Dict[str, Any])
def health_check(
    pipeline: DataProcessingPipeline = Depends(get_data_processing_pipeline),
    validator: DataValidator = Depends(get_data_validator),
    transformation_service: DataTransformationService = Depends(get_transformation_service),
    enrichment_service: DataEnrichmentService = Depends(get_enrichment_service),
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Check health status of all data processing services.
    """
    try:
        health_status = {
            "pipeline": "healthy",
            "validator": "healthy",
            "transformation_service": "healthy", 
            "enrichment_service": "healthy",
            "overall_status": "healthy",
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        # Basic health checks
        if pipeline is None:
            health_status["pipeline"] = "unhealthy"
            health_status["overall_status"] = "degraded"
        
        if validator is None:
            health_status["validator"] = "unhealthy"
            health_status["overall_status"] = "degraded"
            
        if transformation_service is None:
            health_status["transformation_service"] = "unhealthy"
            health_status["overall_status"] = "degraded"
            
        if enrichment_service is None:
            health_status["enrichment_service"] = "unhealthy"
            health_status["overall_status"] = "degraded"
        
        return health_status
    except Exception as e:
        return {
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": pd.Timestamp.now().isoformat()
        }
