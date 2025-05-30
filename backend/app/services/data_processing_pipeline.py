"""
Data Processing Pipeline for Xyra Platform

Integrates validation, transformation, and enrichment services into a unified
data processing pipeline for the AI agent monetization platform.

Provides:
- Unified data processing workflow
- Integration with batch importers
- Configurable processing stages
- Error handling and recovery
- Performance monitoring and reporting
"""

from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import asyncio
from enum import Enum
from dataclasses import dataclass, field
import pandas as pd
import logging
from sqlalchemy.orm import Session

from app.utils.validation import DataValidator
from app.services.data_transformation import (
    DataTransformationService, 
    TransformationRule, 
)
from app.services.data_enrichment import (
    DataEnrichmentService, 
    EnrichmentRule, 
    EnrichmentResult,
    EnrichmentType,
    EnrichmentPriority
)

logger = logging.getLogger(__name__)


class ProcessingStage(str, Enum):
    """Stages in the data processing pipeline"""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    ENRICHMENT = "enrichment"
    FINAL_VALIDATION = "final_validation"
    PERSISTENCE = "persistence"


class PipelineMode(str, Enum):
    """Processing pipeline modes"""
    BATCH = "batch"
    STREAMING = "streaming"
    REAL_TIME = "real_time"


class ProcessingStrategy(str, Enum):
    """Error handling strategies"""
    FAIL_FAST = "fail_fast"
    CONTINUE_ON_ERROR = "continue_on_error"
    RETRY_ON_ERROR = "retry_on_error"


@dataclass
class PipelineConfig:
    """Configuration for the data processing pipeline"""
    name: str
    enabled_stages: List[ProcessingStage] = field(default_factory=lambda: [
        ProcessingStage.VALIDATION,
        ProcessingStage.TRANSFORMATION,
        ProcessingStage.ENRICHMENT,
        ProcessingStage.FINAL_VALIDATION
    ])
    processing_mode: PipelineMode = PipelineMode.BATCH
    error_strategy: ProcessingStrategy = ProcessingStrategy.CONTINUE_ON_ERROR
    max_retries: int = 3
    batch_size: int = 100
    max_concurrent: int = 10
    enable_caching: bool = True
    enable_monitoring: bool = True
    custom_processors: Dict[str, Callable] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result of pipeline processing"""
    success: bool
    total_records: int
    processed_records: int
    failed_records: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stage_results: Dict[ProcessingStage, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: Optional[float] = None
    output_data: Optional[Union[List[Dict[str, Any]], pd.DataFrame]] = None


class DataProcessingPipeline:
    """
    Unified data processing pipeline that orchestrates validation,
    transformation, and enrichment services for the Xyra platform.
    """
    
    def __init__(
        self,
        config: PipelineConfig,
        db_session: Optional[Session] = None,
        validation_framework: Optional[DataValidator] = None,
        transformation_service: Optional[DataTransformationService] = None,
        enrichment_service: Optional[DataEnrichmentService] = None
    ):
        self.config = config
        self.db_session = db_session
        
        # Initialize services
        self.validation_framework = validation_framework or DataValidator()
        self.transformation_service = transformation_service or DataTransformationService(
            self.validation_framework
        )
        self.enrichment_service = enrichment_service or DataEnrichmentService(
            self.validation_framework, 
            self.transformation_service
        )
        
        # Pipeline state
        self.processing_stats = {
            "total_processed": 0,
            "total_errors": 0,
            "stage_performance": {}
        }
        
    async def process_data(
        self, 
        data: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]],
        transformation_rules: Optional[List[TransformationRule]] = None,
        enrichment_rules: Optional[List[EnrichmentRule]] = None,
        custom_config: Optional[PipelineConfig] = None
    ) -> ProcessingResult:
        """
        Process data through the complete pipeline
        
        Args:
            data: Input data to process
            transformation_rules: Optional transformation rules
            enrichment_rules: Optional enrichment rules
            custom_config: Optional custom configuration
            
        Returns:
            ProcessingResult with processed data and metadata
        """
        config = custom_config or self.config
        start_time = datetime.now()
        
        try:
            # Normalize input data
            data_list = self._normalize_input_data(data)
            total_records = len(data_list)
            
            result = ProcessingResult(
                success=True,
                total_records=total_records,
                processed_records=0,
                failed_records=0,
                metadata={
                    "pipeline_name": config.name,
                    "processing_mode": config.processing_mode,
                    "start_time": start_time.isoformat()
                }
            )
            
            # Process data in batches or individually based on mode
            if config.processing_mode == PipelineMode.BATCH:
                processed_data = await self._process_batch_data(
                    data_list, 
                    transformation_rules, 
                    enrichment_rules, 
                    config, 
                    result
                )
            else:
                processed_data = await self._process_streaming_data(
                    data_list, 
                    transformation_rules, 
                    enrichment_rules, 
                    config, 
                    result
                )
            
            result.output_data = processed_data
            result.processing_time = (datetime.now() - start_time).total_seconds()
            result.metadata["end_time"] = datetime.now().isoformat()
            
            # Update pipeline statistics
            self.processing_stats["total_processed"] += result.processed_records
            self.processing_stats["total_errors"] += result.failed_records
            
            logger.info(
                f"Pipeline {config.name} completed: "
                f"{result.processed_records}/{result.total_records} records processed"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                total_records=0,
                processed_records=0,
                failed_records=0,
                errors=[str(e)],
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _process_batch_data(
        self,
        data_list: List[Dict[str, Any]],
        transformation_rules: Optional[List[TransformationRule]],
        enrichment_rules: Optional[List[EnrichmentRule]],
        config: PipelineConfig,
        result: ProcessingResult
    ) -> List[Dict[str, Any]]:
        """Process data in batch mode"""
        processed_data = []
        
        # Process in chunks
        for i in range(0, len(data_list), config.batch_size):
            batch = data_list[i:i + config.batch_size]
            
            try:
                batch_result = await self._process_data_batch(
                    batch, 
                    transformation_rules, 
                    enrichment_rules, 
                    config
                )
                
                processed_data.extend(batch_result["processed_data"])
                result.processed_records += batch_result["processed_count"]
                result.failed_records += batch_result["failed_count"]
                
                if batch_result["errors"]:
                    result.errors.extend(batch_result["errors"])
                if batch_result["warnings"]:
                    result.warnings.extend(batch_result["warnings"])
                    
            except Exception as e:
                logger.error(f"Batch processing failed for chunk {i}: {str(e)}")
                result.errors.append(f"Batch chunk {i} failed: {str(e)}")
                result.failed_records += len(batch)
                
                if config.error_strategy == ProcessingStrategy.FAIL_FAST:
                    raise
        
        return processed_data
    
    async def _process_streaming_data(
        self,
        data_list: List[Dict[str, Any]],
        transformation_rules: Optional[List[TransformationRule]],
        enrichment_rules: Optional[List[EnrichmentRule]],
        config: PipelineConfig,
        result: ProcessingResult
    ) -> List[Dict[str, Any]]:
        """Process data in streaming mode"""
        semaphore = asyncio.Semaphore(config.max_concurrent)
        
        async def process_single_record(data_record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            async with semaphore:
                try:
                    return await self._process_single_record(
                        data_record, 
                        transformation_rules, 
                        enrichment_rules, 
                        config
                    )
                except Exception as e:
                    logger.error(f"Failed to process record: {str(e)}")
                    result.errors.append(str(e))
                    result.failed_records += 1
                    return None
        
        # Process all records concurrently
        tasks = [process_single_record(record) for record in data_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results - exclude None values and exceptions
        processed_data = [r for r in results if r is not None and not isinstance(r, BaseException)]
        result.processed_records = len(processed_data)
        
        return processed_data
    
    async def _process_data_batch(
        self,
        batch: List[Dict[str, Any]],
        transformation_rules: Optional[List[TransformationRule]],
        enrichment_rules: Optional[List[EnrichmentRule]],
        config: PipelineConfig
    ) -> Dict[str, Any]:
        """Process a single batch of data"""
        processed_data = []
        errors = []
        warnings = []
        processed_count = 0
        failed_count = 0
        
        for record in batch:
            try:
                processed_record = await self._process_single_record(
                    record, 
                    transformation_rules, 
                    enrichment_rules, 
                    config
                )
                
                if processed_record:
                    processed_data.append(processed_record)
                    processed_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                errors.append(str(e))
                failed_count += 1
                
                if config.error_strategy == ProcessingStrategy.FAIL_FAST:
                    raise
        
        return {
            "processed_data": processed_data,
            "processed_count": processed_count,
            "failed_count": failed_count,
            "errors": errors,
            "warnings": warnings
        }
    
    async def _process_single_record(
        self,
        record: Dict[str, Any],
        transformation_rules: Optional[List[TransformationRule]],
        enrichment_rules: Optional[List[EnrichmentRule]],
        config: PipelineConfig
    ) -> Optional[Dict[str, Any]]:
        """Process a single data record through all pipeline stages"""
        current_data = record.copy()
        
        for stage in config.enabled_stages:
            try:
                if stage == ProcessingStage.VALIDATION:
                    validation_result = self.validation_framework.validate(current_data, "default")
                    if not validation_result.is_valid:
                        if config.error_strategy == ProcessingStrategy.FAIL_FAST:
                            raise ValueError(f"Validation failed: {validation_result.errors}")
                        logger.warning(f"Validation warnings for record: {validation_result.errors}")
                
                elif stage == ProcessingStage.TRANSFORMATION:
                    if transformation_rules:
                        transformation_result = self.transformation_service.transform_data(
                            current_data, 
                            rules=transformation_rules,
                            validate_input=False,
                            validate_output=False
                        )
                        if transformation_result.success and transformation_result.transformed_data:
                            current_data = transformation_result.transformed_data
                
                elif stage == ProcessingStage.ENRICHMENT:
                    if enrichment_rules:
                        enrichment_result = await self.enrichment_service.enrich_data(
                            current_data,
                            rules=enrichment_rules,
                            validate_input=False,
                            transform_after_enrichment=False
                        )
                        if enrichment_result.success and enrichment_result.enriched_data:
                            current_data = enrichment_result.enriched_data
                
                elif stage == ProcessingStage.FINAL_VALIDATION:
                    final_validation = self.validation_framework.validate(current_data, "default")
                    if not final_validation.is_valid:
                        logger.warning(f"Final validation warnings: {final_validation.errors}")
                
                elif stage == ProcessingStage.PERSISTENCE:
                    # Handle data persistence if needed
                    if self.db_session:
                        await self._persist_data(current_data)
                        
            except Exception as e:
                logger.error(f"Error in stage {stage}: {str(e)}")
                if config.error_strategy == ProcessingStrategy.FAIL_FAST:
                    raise
                elif config.error_strategy == ProcessingStrategy.RETRY_ON_ERROR:
                    # Implement retry logic here
                    pass
        
        return current_data
    
    async def _persist_data(self, data: Dict[str, Any]):
        """Persist processed data to database"""
        # This would be implemented based on specific data models
        # and persistence requirements
        pass
    
    def _normalize_input_data(
        self, 
        data: Union[List[Dict[str, Any]], pd.DataFrame, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Normalize input data to list of dictionaries"""
        if isinstance(data, pd.DataFrame):
            records = data.to_dict('records')
            # Convert Hashable keys to strings to match return type
            return [{str(k): v for k, v in record.items()} for record in records]
        elif isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def create_agent_billing_pipeline(self) -> "DataProcessingPipeline":
        """Create a pipeline specifically configured for agent billing data"""
        config = PipelineConfig(
            name="agent_billing_pipeline",
            enabled_stages=[
                ProcessingStage.VALIDATION,
                ProcessingStage.TRANSFORMATION,
                ProcessingStage.ENRICHMENT,
                ProcessingStage.FINAL_VALIDATION
            ],
            processing_mode=PipelineMode.BATCH,
            error_strategy=ProcessingStrategy.CONTINUE_ON_ERROR,
            batch_size=50,
            max_concurrent=5
        )
        
        # Add specific transformation rules
        transformation_rules = self.transformation_service.create_agent_billing_transformation()
        for rule in transformation_rules:
            self.transformation_service.add_transformation_rule(rule)
        
        # Add specific enrichment rules
        enrichment_rules = self.enrichment_service.create_agent_billing_enrichment_rules()
        for rule in enrichment_rules:
            self.enrichment_service.add_enrichment_rule(rule)
        
        return DataProcessingPipeline(
            config=config,
            db_session=self.db_session,
            validation_framework=self.validation_framework,
            transformation_service=self.transformation_service,
            enrichment_service=self.enrichment_service
        )
    
    def create_integration_data_pipeline(self) -> "DataProcessingPipeline":
        """Create a pipeline specifically configured for integration data"""
        config = PipelineConfig(
            name="integration_data_pipeline",
            enabled_stages=[
                ProcessingStage.VALIDATION,
                ProcessingStage.TRANSFORMATION,
                ProcessingStage.ENRICHMENT
            ],
            processing_mode=PipelineMode.STREAMING,
            error_strategy=ProcessingStrategy.CONTINUE_ON_ERROR,
            max_concurrent=20
        )
        
        # Add specific transformation rules
        transformation_rules = self.transformation_service.create_integration_data_transformation()
        for rule in transformation_rules:
            self.transformation_service.add_transformation_rule(rule)
        
        return DataProcessingPipeline(
            config=config,
            db_session=self.db_session,
            validation_framework=self.validation_framework,
            transformation_service=self.transformation_service,
            enrichment_service=self.enrichment_service
        )
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get pipeline processing statistics"""
        return {
            "total_processed": self.processing_stats["total_processed"],
            "total_errors": self.processing_stats["total_errors"],
            "error_rate": (
                self.processing_stats["total_errors"] / 
                max(self.processing_stats["total_processed"], 1)
            ) * 100,
            "stage_performance": self.processing_stats["stage_performance"]
        }


# Factory function for creating pipeline instances
def create_data_processing_pipeline(
    pipeline_type: str,
    db_session: Optional[Session] = None,
    **kwargs
) -> DataProcessingPipeline:
    """
    Factory function to create configured pipeline instances
    
    Args:
        pipeline_type: Type of pipeline ('agent_billing', 'integration', 'custom')
        db_session: Database session
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured DataProcessingPipeline instance
    """
    if pipeline_type == "agent_billing":
        config = PipelineConfig(
            name="agent_billing_pipeline",
            enabled_stages=[
                ProcessingStage.VALIDATION,
                ProcessingStage.TRANSFORMATION,
                ProcessingStage.ENRICHMENT,
                ProcessingStage.FINAL_VALIDATION
            ],
            processing_mode=PipelineMode.BATCH,
            error_strategy=ProcessingStrategy.CONTINUE_ON_ERROR,
            batch_size=kwargs.get("batch_size", 50),
            max_concurrent=kwargs.get("max_concurrent", 5)
        )
    elif pipeline_type == "integration":
        config = PipelineConfig(
            name="integration_data_pipeline",
            enabled_stages=[
                ProcessingStage.VALIDATION,
                ProcessingStage.TRANSFORMATION,
                ProcessingStage.ENRICHMENT
            ],
            processing_mode=PipelineMode.STREAMING,
            error_strategy=ProcessingStrategy.CONTINUE_ON_ERROR,
            max_concurrent=kwargs.get("max_concurrent", 20)
        )
    else:
        # Custom pipeline configuration
        config = PipelineConfig(
            name=kwargs.get("name", "custom_pipeline"),
            **kwargs
        )
    
    return DataProcessingPipeline(
        config=config,
        db_session=db_session
    )
