"""
Batch import system for processing large volumes of data.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import asyncio
import aiofiles
import logging
from pathlib import Path
import uuid
from app.api import deps
from enum import Enum
import schedule
import threading
import time

logger = logging.getLogger(__name__)

router = APIRouter()

class ImportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ImportJobType(str, Enum):
    ONE_TIME = "one_time"
    SCHEDULED = "scheduled"
    INCREMENTAL = "incremental"

class DataFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    PARQUET = "parquet"
    EXCEL = "excel"

class ImportJob:
    """Represents a batch import job"""
    
    def __init__(
        self,
        job_id: str,
        name: str,
        job_type: ImportJobType,
        data_format: DataFormat,
        source_config: Dict[str, Any],
        transformation_rules: Optional[Dict[str, Any]] = None,
        schedule_config: Optional[Dict[str, Any]] = None
    ):
        self.job_id = job_id
        self.name = name
        self.job_type = job_type
        self.data_format = data_format
        self.source_config = source_config
        self.transformation_rules = transformation_rules or {}
        self.schedule_config = schedule_config or {}
        self.status = ImportStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.records_processed = 0
        self.records_failed = 0
        self.checkpoint_data: Optional[Dict[str, Any]] = None

class BatchImporter:
    """Handles batch import operations"""
    
    def __init__(self):
        self.jobs: Dict[str, ImportJob] = {}
        self.processing_queue = asyncio.Queue()
        self.upload_directory = Path("/tmp/xyra_imports")
        self.upload_directory.mkdir(exist_ok=True)
        
        # Start background job processor
        asyncio.create_task(self._process_jobs())
        
        # Start scheduler for recurring jobs
        self._start_scheduler()
    
    async def create_job(
        self,
        name: str,
        job_type: ImportJobType,
        data_format: DataFormat,
        source_config: Dict[str, Any],
        transformation_rules: Optional[Dict[str, Any]] = None,
        schedule_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new import job"""
        job_id = str(uuid.uuid4())
        
        job = ImportJob(
            job_id=job_id,
            name=name,
            job_type=job_type,
            data_format=data_format,
            source_config=source_config,
            transformation_rules=transformation_rules,
            schedule_config=schedule_config
        )
        
        self.jobs[job_id] = job
        
        # Queue job for processing if it's a one-time job
        if job_type == ImportJobType.ONE_TIME:
            await self.processing_queue.put(job_id)
        
        logger.info(f"Created import job: {job_id}")
        return job_id
    
    async def _process_jobs(self):
        """Background task to process import jobs"""
        while True:
            try:
                job_id = await self.processing_queue.get()
                job = self.jobs.get(job_id)
                
                if job and job.status == ImportStatus.PENDING:
                    await self._execute_job(job)
                
            except Exception as e:
                logger.error(f"Error processing job queue: {e}")
                await asyncio.sleep(5)
    
    async def _execute_job(self, job: ImportJob):
        """Execute an import job"""
        try:
            job.status = ImportStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            logger.info(f"Starting import job: {job.job_id}")
            
            # Load data based on format
            data = await self._load_data(job)
            
            # Apply transformations
            if job.transformation_rules:
                data = await self._transform_data(data, job.transformation_rules)
            
            # Process data in chunks for large datasets
            await self._process_data_chunks(job, data)
            
            job.status = ImportStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(
                f"Completed import job: {job.job_id}, "
                f"Processed: {job.records_processed}, "
                f"Failed: {job.records_failed}"
            )
            
        except Exception as e:
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            logger.error(f"Import job {job.job_id} failed: {e}")
    
    async def _load_data(self, job: ImportJob) -> pd.DataFrame:
        """Load data based on the job's data format"""
        source_config = job.source_config
        file_path = source_config.get("file_path")
        
        if not file_path:
            raise ValueError("File path not provided in source config")
        
        try:
            if job.data_format == DataFormat.CSV:
                return pd.read_csv(file_path)
            elif job.data_format == DataFormat.JSON:
                return pd.read_json(file_path)
            elif job.data_format == DataFormat.PARQUET:
                return pd.read_parquet(file_path)
            elif job.data_format == DataFormat.EXCEL:
                return pd.read_excel(file_path)
            elif job.data_format == DataFormat.XML:
                return self._load_xml_data(file_path)
            else:
                raise ValueError(f"Unsupported data format: {job.data_format}")
                
        except Exception as e:
            raise ValueError(f"Failed to load data: {e}")
    
    def _load_xml_data(self, file_path: str) -> pd.DataFrame:
        """Load XML data and convert to DataFrame"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Simple XML to DataFrame conversion
        # This can be customized based on XML structure
        data = []
        for elem in root:
            row = {}
            for child in elem:
                row[child.tag] = child.text
            data.append(row)
        
        return pd.DataFrame(data)
    
    async def _transform_data(
        self, 
        data: pd.DataFrame, 
        transformation_rules: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply transformation rules to the data"""
        try:
            # Column mapping
            if "column_mapping" in transformation_rules:
                data = data.rename(columns=transformation_rules["column_mapping"])
            
            # Data type conversion
            if "data_types" in transformation_rules:
                for column, dtype in transformation_rules["data_types"].items():
                    if column in data.columns:
                        data[column] = data[column].astype(dtype)
            
            # Filtering
            if "filters" in transformation_rules:
                for filter_rule in transformation_rules["filters"]:
                    column = filter_rule["column"]
                    operator = filter_rule["operator"]
                    value = filter_rule["value"]
                    
                    if operator == "equals":
                        data = data[data[column] == value]
                    elif operator == "not_equals":
                        data = data[data[column] != value]
                    elif operator == "greater_than":
                        data = data[data[column] > value]
                    elif operator == "less_than":
                        data = data[data[column] < value]
            
            # Custom transformations
            if "custom_functions" in transformation_rules:
                for func_config in transformation_rules["custom_functions"]:
                    # Apply custom transformation functions
                    # This would be implemented based on specific needs
                    pass
            
            return data
            
        except Exception as e:
            raise ValueError(f"Data transformation failed: {e}")
    
    async def _process_data_chunks(self, job: ImportJob, data: pd.DataFrame):
        """Process data in chunks to handle large datasets"""
        chunk_size = job.source_config.get("chunk_size", 1000)
        total_records = len(data)
        
        for i in range(0, total_records, chunk_size):
            chunk = data.iloc[i:i + chunk_size]
            
            try:
                # Process chunk (this would be customized based on data type)
                await self._process_chunk(job, chunk)
                job.records_processed += len(chunk)
                
                # Save checkpoint for resumable imports
                job.checkpoint_data = {
                    "last_processed_index": i + len(chunk),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                job.records_failed += len(chunk)
                logger.error(f"Failed to process chunk {i}-{i+len(chunk)}: {e}")
    
    async def _process_chunk(self, job: ImportJob, chunk: pd.DataFrame):
        """Process a data chunk - implement based on specific needs"""
        # This would be customized based on the type of data being imported
        # For example, saving to database, calling APIs, etc.
        
        # Simulate processing
        await asyncio.sleep(0.1)
        
        logger.info(f"Processed chunk of {len(chunk)} records for job {job.job_id}")
    
    def _start_scheduler(self):
        """Start the scheduler for recurring jobs"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def schedule_job(self, job_id: str):
        """Schedule a recurring job"""
        job = self.jobs.get(job_id)
        if not job or job.job_type != ImportJobType.SCHEDULED:
            return
        
        schedule_config = job.schedule_config
        frequency = schedule_config.get("frequency", "daily")
        time_str = schedule_config.get("time", "00:00")
        
        if frequency == "daily":
            schedule.every().day.at(time_str).do(self._execute_scheduled_job, job_id)
        elif frequency == "weekly":
            day = schedule_config.get("day", "monday")
            schedule.every().week.do(self._execute_scheduled_job, job_id)
        elif frequency == "monthly":
            # For monthly, we'll approximate with every 30 days
            schedule.every(30).days.at(time_str).do(self._execute_scheduled_job, job_id)
    
    def _execute_scheduled_job(self, job_id: str):
        """Execute a scheduled job"""
        asyncio.create_task(self.processing_queue.put(job_id))

# Global batch importer instance
batch_importer = BatchImporter()

@router.post("/import/upload")
async def upload_file_for_import(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(deps.get_db)
):
    """Upload a file for batch import"""
    # Validate file type
    allowed_extensions = {".csv", ".json", ".xml", ".parquet", ".xlsx"}
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}"
        )
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = batch_importer.upload_directory / f"{file_id}{file_extension}"
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return {
        "file_id": file_id,
        "filename": file.filename,
        "file_path": str(file_path),
        "size": len(content),
        "upload_time": datetime.utcnow().isoformat()
    }

@router.post("/import/jobs")
async def create_import_job(
    job_config: Dict[str, Any],
    db: Session = Depends(deps.get_db)
):
    """Create a new import job"""
    required_fields = ["name", "job_type", "data_format", "source_config"]
    
    for field in required_fields:
        if field not in job_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    job_id = await batch_importer.create_job(
        name=job_config["name"],
        job_type=ImportJobType(job_config["job_type"]),
        data_format=DataFormat(job_config["data_format"]),
        source_config=job_config["source_config"],
        transformation_rules=job_config.get("transformation_rules"),
        schedule_config=job_config.get("schedule_config")
    )
    
    # Schedule job if it's a recurring job
    if job_config["job_type"] == ImportJobType.SCHEDULED:
        batch_importer.schedule_job(job_id)
    
    return {"job_id": job_id, "status": "created"}

@router.get("/import/jobs/{job_id}")
async def get_import_job_status(
    job_id: str,
    db: Session = Depends(deps.get_db)
):
    """Get import job status and details"""
    job = batch_importer.jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found"
        )
    
    return {
        "job_id": job.job_id,
        "name": job.name,
        "status": job.status,
        "job_type": job.job_type,
        "data_format": job.data_format,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "records_processed": job.records_processed,
        "records_failed": job.records_failed,
        "error_message": job.error_message,
        "checkpoint_data": job.checkpoint_data
    }

@router.get("/import/jobs")
async def list_import_jobs(
    status: Optional[ImportStatus] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(deps.get_db)
):
    """List import jobs with optional filtering"""
    jobs = list(batch_importer.jobs.values())
    
    if status:
        jobs = [job for job in jobs if job.status == status]
    
    # Sort by creation time (newest first)
    jobs.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    paginated_jobs = jobs[offset:offset + limit]
    
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "name": job.name,
                "status": job.status,
                "job_type": job.job_type,
                "created_at": job.created_at,
                "records_processed": job.records_processed,
                "records_failed": job.records_failed
            }
            for job in paginated_jobs
        ],
        "total": len(jobs),
        "limit": limit,
        "offset": offset
    }

@router.post("/import/jobs/{job_id}/retry")
async def retry_import_job(
    job_id: str,
    db: Session = Depends(deps.get_db)
):
    """Retry a failed import job"""
    job = batch_importer.jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found"
        )
    
    if job.status not in [ImportStatus.FAILED, ImportStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job can only be retried if it's failed or cancelled"
        )
    
    # Reset job status and queue for processing
    job.status = ImportStatus.PENDING
    job.error_message = None
    job.records_processed = 0
    job.records_failed = 0
    
    await batch_importer.processing_queue.put(job_id)
    
    return {"status": "queued_for_retry"}

@router.delete("/import/jobs/{job_id}")
async def cancel_import_job(
    job_id: str,
    db: Session = Depends(deps.get_db)
):
    """Cancel an import job"""
    job = batch_importer.jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import job not found"
        )
    
    if job.status == ImportStatus.PROCESSING:
        job.status = ImportStatus.CANCELLED
        job.completed_at = datetime.utcnow()
    
    return {"status": "cancelled"}
