"""
Enhanced Batch Importer for Xyra Platform

Integrates the comprehensive data processing pipeline (validation, transformation, 
enrichment) with the existing batch import system to provide enterprise-grade
data processing capabilities for the AI agent monetization platform.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List, Union
import pandas as pd
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import uuid

from app.api import deps
from app.integration.batch_importers import ImportJob, ImportStatus, ImportJobType, DataFormat
from app.services.data_processing_pipeline import (
    DataProcessingPipeline, 
    PipelineConfig, 
    ProcessingStage,
    PipelineMode,
    ProcessingStrategy,
    create_data_processing_pipeline
)
from app.services.data_transformation import (
    TransformationRule, 
    TransformationType,
    create_currency_transformation_rule,
    create_email_normalization_rule
)
from app.services.data_enrichment import (
    EnrichmentRule, 
    EnrichmentType,
    EnrichmentPriority,
    create_timestamp_enrichment_rule,
    create_data_quality_enrichment_rule
)
from app.utils.validation import DataValidator

logger = logging.getLogger(__name__)

router = APIRouter()


class EnhancedImportJob(ImportJob):
    """Enhanced import job with data processing pipeline integration"""
    
    def __init__(
        self,
        job_id: str,
        name: str,
        job_type: ImportJobType,
        data_format: DataFormat,
        source_config: Dict[str, Any],
        pipeline_config: Optional[PipelineConfig] = None,
        transformation_rules: Optional[List[TransformationRule]] = None,
        enrichment_rules: Optional[List[EnrichmentRule]] = None,
        **kwargs
    ):
        super().__init__(
            job_id=job_id,
            name=name,
            job_type=job_type,
            data_format=data_format,
            source_config=source_config,
            **kwargs
        )
        
        # Enhanced processing capabilities
        self.pipeline_config = pipeline_config
        self.transformation_rules = transformation_rules or []
        self.enrichment_rules = enrichment_rules or []
        self.processing_pipeline: Optional[DataProcessingPipeline] = None
        self.processing_results: Dict[str, Any] = {}
        
    def initialize_pipeline(self, db_session: Session):
        """Initialize the data processing pipeline for this job"""
        if self.pipeline_config:
            self.processing_pipeline = DataProcessingPipeline(
                config=self.pipeline_config,
                db_session=db_session
            )
        else:
            # Use default pipeline based on job characteristics
            pipeline_type = self._determine_pipeline_type()
            self.processing_pipeline = create_data_processing_pipeline(
                pipeline_type=pipeline_type,
                db_session=db_session
            )
            
    def _determine_pipeline_type(self) -> str:
        """Determine appropriate pipeline type based on job characteristics"""
        # Analyze source config and data format to determine best pipeline
        if "agent" in self.name.lower() or "billing" in self.name.lower():
            return "agent_billing"
        elif "integration" in self.name.lower() or "webhook" in self.name.lower():
            return "integration"
        else:
            return "custom"


class EnhancedBatchImportManager:
    """
    Enhanced batch import manager with comprehensive data processing capabilities
    """
    
    def __init__(self):
        self.jobs: Dict[str, EnhancedImportJob] = {}
        self.processing_queue = asyncio.Queue()
        self.validation_framework = DataValidator()
        
        # Start background processing
        asyncio.create_task(self._process_jobs())
    
    async def create_enhanced_import_job(
        self,
        name: str,
        job_type: ImportJobType,
        data_format: DataFormat,
        source_config: Dict[str, Any],
        pipeline_config: Optional[Dict[str, Any]] = None,
        transformation_config: Optional[Dict[str, Any]] = None,
        enrichment_config: Optional[Dict[str, Any]] = None,
        db_session: Optional[Session] = None
    ) -> str:
        """
        Create an enhanced import job with data processing pipeline
        
        Args:
            name: Job name
            job_type: Type of import job
            data_format: Input data format
            source_config: Source configuration
            pipeline_config: Pipeline configuration
            transformation_config: Transformation rules configuration
            enrichment_config: Enrichment rules configuration
            db_session: Database session
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Parse configurations
        parsed_pipeline_config = self._parse_pipeline_config(pipeline_config)
        transformation_rules = self._parse_transformation_config(transformation_config)
        enrichment_rules = self._parse_enrichment_config(enrichment_config)
        
        # Create enhanced job
        job = EnhancedImportJob(
            job_id=job_id,
            name=name,
            job_type=job_type,
            data_format=data_format,
            source_config=source_config,
            pipeline_config=parsed_pipeline_config,
            transformation_rules=transformation_rules,
            enrichment_rules=enrichment_rules
        )
        
        # Initialize pipeline
        if db_session:
            job.initialize_pipeline(db_session)
        
        self.jobs[job_id] = job
        
        # Queue job for processing
        if job_type == ImportJobType.ONE_TIME:
            await self.processing_queue.put(job_id)
        
        logger.info(f"Created enhanced import job: {job_id}")
        return job_id
    
    def _parse_pipeline_config(self, config: Optional[Dict[str, Any]]) -> Optional[PipelineConfig]:
        """Parse pipeline configuration from dict"""
        if not config:
            return None
            
        return PipelineConfig(
            name=config.get("name", "default_pipeline"),
            enabled_stages=[ProcessingStage(stage) for stage in config.get("enabled_stages", [])],
            processing_mode=PipelineMode(config.get("processing_mode", "batch")),
            error_strategy=ProcessingStrategy(config.get("error_strategy", "continue_on_error")),
            max_retries=config.get("max_retries", 3),
            batch_size=config.get("batch_size", 100),
            max_concurrent=config.get("max_concurrent", 10),
            enable_caching=config.get("enable_caching", True),
            enable_monitoring=config.get("enable_monitoring", True)
        )
    
    def _parse_transformation_config(
        self, 
        config: Optional[Dict[str, Any]]
    ) -> List[TransformationRule]:
        """Parse transformation rules from configuration"""
        if not config:
            return []
            
        rules = []
        
        # Field mappings
        if "field_mappings" in config:
            for source, target in config["field_mappings"].items():
                rules.append(TransformationRule(
                    name=f"map_{source}_to_{target}",
                    transformation_type=TransformationType.FIELD_MAPPING,
                    source_field=source,
                    target_field=target,
                    description=f"Map {source} field to {target}"
                ))
        
        # Type conversions
        if "type_conversions" in config:
            for field, target_type in config["type_conversions"].items():
                rules.append(TransformationRule(
                    name=f"convert_{field}_type",
                    transformation_type=TransformationType.TYPE_CONVERSION,
                    source_field=field,
                    parameters={"target_type": target_type},
                    description=f"Convert {field} to {target_type}"
                ))
        
        # Normalization rules
        if "normalizations" in config:
            for field, normalization_type in config["normalizations"].items():
                rules.append(TransformationRule(
                    name=f"normalize_{field}",
                    transformation_type=TransformationType.VALUE_NORMALIZATION,
                    source_field=field,
                    parameters={"normalization_type": normalization_type},
                    description=f"Normalize {field} using {normalization_type}"
                ))
        
        # Business logic rules
        if "business_rules" in config:
            for rule_config in config["business_rules"]:
                # This would be implemented based on specific business logic needs
                pass
        
        return rules
    
    def _parse_enrichment_config(
        self, 
        config: Optional[Dict[str, Any]]
    ) -> List[EnrichmentRule]:
        """Parse enrichment rules from configuration"""
        if not config:
            return []
            
        rules = []
        
        # Calculation enrichments
        if "calculations" in config:
            for calc_config in config["calculations"]:
                rules.append(EnrichmentRule(
                    name=calc_config.get("name", "calculation"),
                    enrichment_type=EnrichmentType.CALCULATION,
                    source_fields=calc_config.get("source_fields", []),
                    target_fields=calc_config.get("target_fields", []),
                    parameters={
                        "calculation_type": calc_config.get("calculation_type", "sum")
                    },
                    priority=EnrichmentPriority(calc_config.get("priority", "medium")),
                    description=calc_config.get("description", "")
                ))
        
        # Geolocation enrichments
        if "geolocation" in config and config["geolocation"]["enabled"]:
            rules.append(EnrichmentRule(
                name="geolocation_enrichment",
                enrichment_type=EnrichmentType.GEO_LOCATION,
                source_fields=config["geolocation"].get("source_fields", ["ip_address"]),
                target_fields=config["geolocation"].get("target_fields", ["country", "city"]),
                priority=EnrichmentPriority.MEDIUM,
                cache_ttl=3600,
                description="Enrich with geolocation data"
            ))
        
        # Audit enrichments
        if "audit" in config and config["audit"]["enabled"]:
            rules.append(EnrichmentRule(
                name="audit_enrichment",
                enrichment_type=EnrichmentType.AUDIT,
                source_fields=[],
                target_fields=config["audit"].get("target_fields", ["audit_timestamp"]),
                priority=EnrichmentPriority.LOW,
                description="Add audit trail information"
            ))
        
        return rules
    
    async def _process_jobs(self):
        """Background task to process import jobs"""
        while True:
            try:
                job_id = await self.processing_queue.get()
                job = self.jobs.get(job_id)
                
                if job and job.status == ImportStatus.PENDING:
                    await self._execute_enhanced_job(job)
                
            except Exception as e:
                logger.error(f"Error processing job queue: {e}")
                await asyncio.sleep(5)
    
    async def _execute_enhanced_job(self, job: EnhancedImportJob):
        """Execute an enhanced import job with full data processing pipeline"""
        try:
            job.status = ImportStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            logger.info(f"Starting enhanced import job: {job.job_id}")
            
            # Load data
            data = await self._load_data(job)
            
            # Process data through pipeline if available
            if job.processing_pipeline:
                processing_result = await job.processing_pipeline.process_data(
                    data=data,
                    transformation_rules=job.transformation_rules,
                    enrichment_rules=job.enrichment_rules
                )
                
                job.processing_results = {
                    "success": processing_result.success,
                    "total_records": processing_result.total_records,
                    "processed_records": processing_result.processed_records,
                    "failed_records": processing_result.failed_records,
                    "errors": processing_result.errors,
                    "warnings": processing_result.warnings,
                    "processing_time": processing_result.processing_time,
                    "metadata": processing_result.metadata
                }
                
                if processing_result.success and processing_result.output_data is not None:
                    # Use processed data for final storage
                    final_data = processing_result.output_data
                else:
                    # Fallback to original data if processing failed
                    final_data = data
                    logger.warning(f"Pipeline processing failed for job {job.job_id}, using original data")
            else:
                # Fallback to basic processing
                final_data = data
                job.processing_results = {
                    "success": True,
                    "total_records": len(data) if isinstance(data, list) else len(data.index),
                    "processed_records": len(data) if isinstance(data, list) else len(data.index),
                    "failed_records": 0,
                    "processing_time": 0,
                    "note": "Basic processing - no pipeline configured"
                }
            
            # Store processed data (this would integrate with your data storage layer)
            await self._store_processed_data(job, final_data)
            
            job.status = ImportStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"Enhanced import job {job.job_id} completed successfully")
            
        except Exception as e:
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            logger.error(f"Enhanced import job {job.job_id} failed: {e}")
    
    async def _load_data(self, job: EnhancedImportJob) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """Load data based on job configuration"""
        # This would implement the actual data loading logic
        # For now, return sample data based on format
        if job.data_format == DataFormat.CSV:
            return pd.DataFrame([
                {"id": 1, "name": "Agent 1", "cost": 10.50},
                {"id": 2, "name": "Agent 2", "cost": 15.75}
            ])
        elif job.data_format == DataFormat.JSON:
            return [
                {"id": 1, "name": "Agent 1", "cost": 10.50},
                {"id": 2, "name": "Agent 2", "cost": 15.75}
            ]
        else:
            return pd.DataFrame()
    
    async def _store_processed_data(
        self, 
        job: EnhancedImportJob, 
        data: Union[pd.DataFrame, List[Dict[str, Any]]]
    ):
        """Store the processed data"""
        # This would implement the actual data storage logic
        # Integration with your database models and storage layer
        logger.info(f"Storing {len(data)} processed records for job {job.job_id}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of an import job"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "name": job.name,
            "status": job.status,
            "job_type": job.job_type,
            "data_format": job.data_format,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "processing_results": job.processing_results,
            "error_message": getattr(job, 'error_message', None),
            "pipeline_configured": job.processing_pipeline is not None
        }


# Initialize the enhanced batch import manager
enhanced_import_manager = EnhancedBatchImportManager()


@router.post("/enhanced-import/create")
async def create_enhanced_import_job(
    job_config: Dict[str, Any],
    db: Session = Depends(deps.get_db)
):
    """
    Create an enhanced import job with full data processing pipeline
    
    Example job_config:
    {
        "name": "agent_billing_import",
        "job_type": "one_time",
        "data_format": "csv",
        "source_config": {
            "file_path": "/path/to/data.csv"
        },
        "pipeline_config": {
            "name": "agent_billing_pipeline",
            "enabled_stages": ["validation", "transformation", "enrichment"],
            "processing_mode": "batch",
            "batch_size": 100
        },
        "transformation_config": {
            "field_mappings": {
                "external_agent_id": "agent_id"
            },
            "type_conversions": {
                "cost": "decimal"
            },
            "normalizations": {
                "agent_name": "trim"
            }
        },
        "enrichment_config": {
            "calculations": [
                {
                    "name": "calculate_total_cost",
                    "source_fields": ["base_cost", "additional_cost"],
                    "target_fields": ["total_cost"],
                    "calculation_type": "sum"
                }
            ],
            "audit": {
                "enabled": true,
                "target_fields": ["processed_at", "processed_by"]
            }
        }
    }
    """
    try:
        job_id = await enhanced_import_manager.create_enhanced_import_job(
            name=job_config["name"],
            job_type=ImportJobType(job_config["job_type"]),
            data_format=DataFormat(job_config["data_format"]),
            source_config=job_config["source_config"],
            pipeline_config=job_config.get("pipeline_config"),
            transformation_config=job_config.get("transformation_config"),
            enrichment_config=job_config.get("enrichment_config"),
            db_session=db
        )
        
        return {
            "job_id": job_id,
            "message": "Enhanced import job created successfully",
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"Failed to create enhanced import job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create import job: {str(e)}"
        )


@router.get("/enhanced-import/{job_id}/status")
async def get_enhanced_job_status(job_id: str):
    """Get detailed status of an enhanced import job"""
    job_status = enhanced_import_manager.get_job_status(job_id)
    
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job_status


@router.get("/enhanced-import/jobs")
async def list_enhanced_jobs():
    """List all enhanced import jobs"""
    jobs = []
    for job_id, job in enhanced_import_manager.jobs.items():
        jobs.append({
            "job_id": job_id,
            "name": job.name,
            "status": job.status,
            "job_type": job.job_type,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "pipeline_configured": job.processing_pipeline is not None
        })
    
    return {"jobs": jobs}


@router.post("/enhanced-import/presets/agent-billing")
async def create_agent_billing_import_preset(
    source_config: Dict[str, Any],
    custom_config: Optional[Dict[str, Any]] = None,
    db: Session = Depends(deps.get_db)
):
    """
    Create an agent billing import job with preset configuration
    """
    job_config = {
        "name": f"agent_billing_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "job_type": "one_time",
        "data_format": source_config.get("format", "csv"),
        "source_config": source_config,
        "pipeline_config": {
            "name": "agent_billing_pipeline",
            "enabled_stages": ["validation", "transformation", "enrichment", "final_validation"],
            "processing_mode": "batch",
            "batch_size": 50,
            "error_strategy": "continue_on_error"
        },
        "transformation_config": {
            "field_mappings": {
                "external_agent_id": "agent_id",
                "agent_external_id": "agent_id"
            },
            "type_conversions": {
                "cost": "decimal",
                "timestamp": "datetime"
            },
            "normalizations": {
                "agent_name": "trim",
                "email": "normalize_email"
            }
        },
        "enrichment_config": {
            "calculations": [
                {
                    "name": "calculate_usage_metrics",
                    "source_fields": ["requests_count", "processing_time"],
                    "target_fields": ["average_response_time"],
                    "calculation_type": "average"
                }
            ],
            "audit": {
                "enabled": True,
                "target_fields": ["processed_at", "processed_by", "data_quality_score"]
            }
        }
    }
    
    # Apply custom overrides
    if custom_config:
        job_config.update(custom_config)
    
    job_id = await enhanced_import_manager.create_enhanced_import_job(**job_config, db_session=db)
    
    return {
        "job_id": job_id,
        "message": "Agent billing import job created with preset configuration",
        "preset": "agent_billing"
    }
