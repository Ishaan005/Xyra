"""
Integration layer models for connectors, webhooks, and events.
These models provide persistence for the integration layer with proper multi-tenancy.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import BaseModel


class IntegrationConnector(BaseModel):
    """
    Stores configuration and credentials for external system connections.
    Provides persistence for the ConnectorManager with multi-tenancy support.
    """
    __tablename__ = 'integration_connectors'  # type: ignore[assignment]
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    connector_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    connector_type = Column(String(50), nullable=False)  # 'rest_api', 'graphql', 'webhook'
    
    # Configuration and authentication
    config = Column(JSONB, nullable=False, default={})
    auth_config = Column(JSONB, nullable=False, default={})
    
    # Status and health monitoring
    status = Column(String(50), nullable=False, default='active')  # 'active', 'inactive', 'error'
    health_status = Column(String(50), default='unknown')  # 'healthy', 'unhealthy', 'unknown'
    last_health_check = Column(DateTime, nullable=True)
    
    # Metrics and monitoring
    metrics = Column(JSONB, default={})
    
    # Relationships
    organization = relationship("Organization", back_populates="integration_connectors")
    
    def __str__(self) -> str:
        return f"IntegrationConnector(name={self.name}, type={self.connector_type}, org_id={self.organization_id})"


class IntegrationWebhook(BaseModel):
    """
    Manages webhook endpoint registrations with security and monitoring.
    Provides persistence for webhook configurations with retry logic.
    """
    __tablename__ = 'integration_webhooks'  # type: ignore[assignment]
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    endpoint_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    url = Column(String(1024), nullable=False)
    secret = Column(String(255), nullable=False)
    
    # Event filtering
    event_types = Column(ARRAY(String(100)), nullable=False)
    
    # Status and configuration
    status = Column(String(50), nullable=False, default='active')  # 'active', 'inactive', 'paused'
    retry_config = Column(JSONB, default={
        'max_retries': 3,
        'retry_delay': 60,  # seconds
        'backoff_multiplier': 2
    })
    
    # Monitoring
    last_triggered_at = Column(DateTime, nullable=True)
    metrics = Column(JSONB, default={
        'total_calls': 0,
        'successful_calls': 0,
        'failed_calls': 0,
        'avg_response_time': 0
    })
    
    # Relationships
    organization = relationship("Organization", back_populates="integration_webhooks")
    
    def __str__(self) -> str:
        return f"IntegrationWebhook(name={self.name}, url={self.url}, org_id={self.organization_id})"


class IntegrationEvent(BaseModel):
    """
    Central event store for all integration data.
    Critical for outcome-based billing and audit trails.
    """
    __tablename__ = 'integration_events'  # type: ignore[assignment]
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=True)
    
    # Source information
    source_type = Column(String(50), nullable=False)  # 'webhook', 'connector', 'stream', 'batch', 'api'
    source_id = Column(String(255), nullable=False)  # ID of the webhook/connector/etc
    
    # Event classification
    event_type = Column(String(100), nullable=False)  # 'activity', 'cost', 'outcome', 'health_check'
    external_reference_id = Column(String(255), nullable=True)
    
    # Event timing
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Event data
    raw_data = Column(JSONB, nullable=False)
    processed_data = Column(JSONB, nullable=True)
    
    # Processing status
    processing_status = Column(String(50), default='pending')  # 'pending', 'processed', 'failed', 'skipped'
    processing_attempts = Column(Integer, default=0)
    last_processing_error = Column(Text, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="integration_events")
    agent = relationship("Agent", back_populates="integration_events")
    
    def __str__(self) -> str:
        return f"IntegrationEvent(type={self.event_type}, source={self.source_type}, status={self.processing_status})"


class IntegrationStream(BaseModel):
    """
    Manages streaming data connections for real-time integration.
    Extends the existing streaming capabilities with persistence.
    """
    __tablename__ = 'integration_streams'  # type: ignore[assignment]
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    stream_id = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    
    # Stream configuration
    protocol = Column(String(50), nullable=False)  # 'kafka', 'redis', 'websocket', 'sse'
    config = Column(JSONB, nullable=False, default={})
    
    # Status and monitoring
    status = Column(String(50), nullable=False, default='active')  # 'active', 'inactive', 'error'
    
    # Metrics
    metrics = Column(JSONB, default={
        'messages_processed': 0,
        'messages_failed': 0,
        'last_message_at': None,
        'avg_processing_time': 0
    })
    
    # Relationships
    organization = relationship("Organization", back_populates="integration_streams")
    
    def __str__(self) -> str:
        return f"IntegrationStream(name={self.name}, protocol={self.protocol}, org_id={self.organization_id})"
