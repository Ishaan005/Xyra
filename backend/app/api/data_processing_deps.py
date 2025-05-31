"""
Data Processing Dependencies for FastAPI

Provides dependency injection for data processing services including
validation, transformation, enrichment, and pipeline orchestration.
"""

from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.data_processing_pipeline import DataProcessingPipeline, PipelineConfig
from app.services.data_transformation import DataTransformationService
from app.services.data_enrichment import DataEnrichmentService
from app.utils.validation import DataValidator


@lru_cache()
def get_data_validator() -> DataValidator:
    """
    Get singleton instance of DataValidator
    """
    return DataValidator()


@lru_cache()
def get_transformation_service() -> DataTransformationService:
    """
    Get singleton instance of DataTransformationService
    """
    return DataTransformationService(validation_framework=DataValidator())


@lru_cache()
def get_enrichment_service() -> DataEnrichmentService:
    """
    Get singleton instance of DataEnrichmentService
    """
    return DataEnrichmentService(
        validation_framework=DataValidator(),
        transformation_service=DataTransformationService(validation_framework=DataValidator())
    )


def get_data_processing_pipeline(
    db: Session = Depends(get_db),
    validator: DataValidator = Depends(get_data_validator),
    transformation_service: DataTransformationService = Depends(get_transformation_service),
    enrichment_service: DataEnrichmentService = Depends(get_enrichment_service)
) -> DataProcessingPipeline:
    """
    Get configured DataProcessingPipeline instance with all services
    """
    config = PipelineConfig(name="default_pipeline")
    return DataProcessingPipeline(
        config=config,
        db_session=db,
        validation_framework=validator,
        transformation_service=transformation_service,
        enrichment_service=enrichment_service
    )


def get_data_quality_metrics() -> dict:
    """
    Get current data quality metrics
    """
    # This will be populated with actual metrics from pipeline execution
    return {
        "validation_success_rate": 0.95,
        "transformation_success_rate": 0.98,
        "enrichment_success_rate": 0.92,
        "pipeline_completion_rate": 0.90,
        "avg_processing_time_ms": 150,
        "error_rate": 0.05
    }
