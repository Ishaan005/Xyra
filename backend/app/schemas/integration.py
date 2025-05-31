"""
Pydantic schemas for integration layer endpoints.
Provides request/response models for connectors, webhooks, events, and streams.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ConnectorTypeEnum(str, Enum):
    """Supported connector types"""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    CUSTOM = "custom"


class AuthTypeEnum(str, Enum):
    """Supported authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


class ConnectorStatusEnum(str, Enum):
    """Connector status options"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class AuthConfigSchema(BaseModel):
    """Authentication configuration schema"""
    type: AuthTypeEnum = AuthTypeEnum.NONE
    # For API_KEY auth
    key: Optional[str] = None
    value: Optional[str] = None
    # For BEARER_TOKEN auth
    token: Optional[str] = None
    # For BASIC_AUTH auth
    username: Optional[str] = None
    password: Optional[str] = None
    # For OAUTH2 auth
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token_url: Optional[str] = None
    scopes: Optional[List[str]] = None


class ConnectorConfigSchema(BaseModel):
    """Connector configuration schema"""
    # Common configuration
    timeout: Optional[int] = Field(default=30, ge=1, le=300)
    connect_timeout: Optional[int] = Field(default=10, ge=1, le=60)
    verify_ssl: Optional[bool] = True
    headers: Optional[Dict[str, str]] = None
    
    # REST API specific
    base_url: Optional[str] = None
    health_endpoint: Optional[str] = "/health"
    
    # GraphQL specific
    endpoint: Optional[str] = None
    
    # Authentication
    auth: Optional[AuthConfigSchema] = None


class HealthStatusSchema(BaseModel):
    """Connector health status"""
    is_healthy: bool
    last_check: Optional[datetime] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    consecutive_failures: int = 0


class MetricsSchema(BaseModel):
    """Connector metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    data_extracted: int = 0


class ConnectorBase(BaseModel):
    """Base connector schema"""
    name: str = Field(..., min_length=1, max_length=255)
    connector_type: ConnectorTypeEnum
    config: ConnectorConfigSchema
    description: Optional[str] = Field(None, max_length=1000)


class ConnectorCreate(ConnectorBase):
    """Schema for creating connectors"""
    connector_id: str = Field(..., min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9_-]+$')
    
    @validator('connector_id')
    def validate_connector_id(cls, v:str):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Connector ID must contain only alphanumeric characters, underscores, and hyphens')
        return v


class ConnectorUpdate(BaseModel):
    """Schema for updating connectors"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    config: Optional[ConnectorConfigSchema] = None
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ConnectorStatusEnum] = None
    health_status: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class ConnectorResponse(ConnectorBase):
    """Schema for connector responses"""
    id: str
    connector_id: str
    organization_id: int
    status: ConnectorStatusEnum
    health_status: Optional[str] = None
    last_health_check: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConnectorDetailResponse(ConnectorResponse):
    """Detailed connector response with live health and metrics"""
    health: Optional[HealthStatusSchema] = None
    live_metrics: Optional[MetricsSchema] = None


class ExtractionConfigSchema(BaseModel):
    """Data extraction configuration"""
    # REST API specific
    endpoint: Optional[str] = None
    method: Optional[str] = Field(default="GET", pattern=r'^(GET|POST|PUT|PATCH|DELETE)$')
    params: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    data_path: Optional[str] = None
    field_mapping: Optional[Dict[str, str]] = None
    
    # GraphQL specific
    query: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class ExtractionResponse(BaseModel):
    """Data extraction response"""
    connector_id: str
    records_extracted: int
    data: List[Dict[str, Any]]
    extraction_time: datetime
    execution_time_ms: Optional[float] = None


# Event schemas for billing integration
class EventCreate(BaseModel):
    """Schema for creating integration events"""
    source_type: str = Field(..., max_length=50)
    source_id: str = Field(..., max_length=255)
    event_type: str = Field(..., max_length=50)
    raw_data: Dict[str, Any]
    processed_data: Optional[Dict[str, Any]] = None
    agent_id: Optional[int] = None


class EventResponse(BaseModel):
    """Schema for event responses"""
    id: str
    organization_id: int
    source_type: str
    source_id: str
    event_type: str
    raw_data: Dict[str, Any]
    processed_data: Optional[Dict[str, Any]]
    agent_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bulk operations
class BulkOperationRequest(BaseModel):
    """Schema for bulk operations on connectors"""
    operation: str = Field(..., pattern=r'^(test|start|stop|delete)$')
    connector_ids: List[str] = Field(...)
    
    @validator('connector_ids')
    def validate_connector_ids(cls, v):
        if len(v) < 1:
            raise ValueError('At least one connector ID is required')
        if len(v) > 100:
            raise ValueError('Maximum 100 connector IDs allowed')
        return v


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation responses"""
    operation: str
    total_count: int
    successful_count: int
    failed_count: int
    results: List[Dict[str, Any]]


# Connector cloning
class ConnectorCloneRequest(BaseModel):
    """Schema for cloning connectors"""
    source_connector_id: str = Field(..., min_length=1, max_length=255)
    new_connector_id: str = Field(..., min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9_-]+$')
    new_name: str = Field(..., min_length=1, max_length=255)
    config_overrides: Optional[Dict[str, Any]] = None


# Connector templates
class ConnectorTemplate(BaseModel):
    """Schema for connector templates"""
    name: str
    description: str
    connector_type: ConnectorTypeEnum
    config_template: ConnectorConfigSchema
    example_extraction_config: Optional[ExtractionConfigSchema] = None


# Webhook schemas (for future implementation)
class WebhookEventType(str, Enum):
    """Supported webhook event types"""
    AGENT_ACTIVITY = "agent.activity"
    AGENT_COST = "agent.cost"  
    AGENT_OUTCOME = "agent.outcome"
    BILLING_EVENT = "billing.event"
    INTEGRATION_EVENT = "integration.event"
    SYSTEM_HEALTH = "system.health"


class WebhookStatus(str, Enum):
    """Webhook status options"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


class RetryConfigSchema(BaseModel):
    """Webhook retry configuration"""
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=60, ge=1, le=3600)  # seconds
    backoff_multiplier: float = Field(default=2.0, ge=1.0, le=10.0)


class WebhookBase(BaseModel):
    """Base webhook schema"""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., pattern=r'^https?://.+')
    event_types: List[WebhookEventType]
    description: Optional[str] = Field(None, max_length=1000)
    retry_config: Optional[RetryConfigSchema] = None


class WebhookCreate(WebhookBase):
    """Schema for creating webhooks"""
    endpoint_id: str = Field(..., min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9_-]+$')


class WebhookUpdate(BaseModel):
    """Schema for updating webhooks"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, pattern=r'^https?://.+')
    event_types: Optional[List[WebhookEventType]] = None
    description: Optional[str] = Field(None, max_length=1000)
    retry_config: Optional[RetryConfigSchema] = None
    status: Optional[WebhookStatus] = None


class WebhookResponse(WebhookBase):
    """Schema for webhook responses"""
    id: str
    endpoint_id: str
    organization_id: int
    status: WebhookStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Stream schemas (for future implementation)
class StreamCreate(BaseModel):
    """Schema for creating stream consumers"""
    stream_id: str = Field(..., min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9_-]+$')
    name: str = Field(..., min_length=1, max_length=255)
    source_config: Dict[str, Any]
    processing_config: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=1000)


class StreamResponse(BaseModel):
    """Schema for stream responses"""
    id: str
    stream_id: str
    organization_id: int
    name: str
    source_config: Dict[str, Any]
    processing_config: Optional[Dict[str, Any]]
    status: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
