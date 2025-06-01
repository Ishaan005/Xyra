"""
Integration service layer for managing connectors, webhooks, events, and streams.
Provides CRUD operations with organization-based multi-tenancy and business logic.
"""
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.models.integration import IntegrationConnector, IntegrationWebhook, IntegrationEvent, IntegrationStream
from app.schemas.integration import (
    ConnectorCreate, ConnectorUpdate, 
    WebhookCreate, WebhookUpdate,
    EventCreate,
    StreamCreate
)

logger = logging.getLogger(__name__)

# ===== CONNECTOR OPERATIONS =====

def get_connector(
    db: Session, 
    connector_id: str, 
    organization_id: int
) -> Optional[IntegrationConnector]:
    """Get a connector by ID and organization"""
    return db.query(IntegrationConnector).filter(
        and_(
            IntegrationConnector.connector_id == connector_id,
            IntegrationConnector.organization_id == organization_id
        )
    ).first()


def get_connectors(
    db: Session, 
    organization_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
) -> List[IntegrationConnector]:
    """Get all connectors for an organization with optional filtering"""
    query = db.query(IntegrationConnector).filter(
        IntegrationConnector.organization_id == organization_id
    )
    
    if status:
        query = query.filter(IntegrationConnector.status == status)
    
    return query.offset(skip).limit(limit).all()


def create_connector(
    db: Session, 
    connector_in: ConnectorCreate, 
    organization_id: int
) -> IntegrationConnector:
    """Create a new connector"""
    connector = IntegrationConnector(
        id=str(uuid.uuid4()),
        connector_id=connector_in.connector_id,
        organization_id=organization_id,
        name=connector_in.name,
        connector_type=connector_in.connector_type,
        config=connector_in.config.model_dump() if connector_in.config else {},
        description=connector_in.description,
        status="inactive",  # Start as inactive until configured
        health_status="unknown",
        metrics={}
    )
    
    db.add(connector)
    db.commit()
    db.refresh(connector)
    
    logger.info(f"Created connector {connector_in.connector_id} for organization {organization_id}")
    return connector


def update_connector(
    db: Session, 
    connector_id: str, 
    organization_id: int, 
    connector_update: ConnectorUpdate
) -> Optional[IntegrationConnector]:
    """Update an existing connector"""
    connector = get_connector(db, connector_id, organization_id)
    if not connector:
        return None
    
    # Update fields
    update_data = connector_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "config" and value:
            setattr(connector, field, value.model_dump())
        else:
            setattr(connector, field, value)
    
    # The updated_at field will be automatically updated by the BaseModel
    db.commit()
    db.refresh(connector)
    
    logger.info(f"Updated connector {connector_id} for organization {organization_id}")
    return connector


def delete_connector(
    db: Session, 
    connector_id: str, 
    organization_id: int
) -> Optional[IntegrationConnector]:
    """Delete a connector"""
    connector = get_connector(db, connector_id, organization_id)
    if not connector:
        return None
    
    db.delete(connector)
    db.commit()
    
    logger.info(f"Deleted connector {connector_id} for organization {organization_id}")
    return connector


# ===== WEBHOOK OPERATIONS =====

def get_webhook(
    db: Session,
    endpoint_id: str,
    organization_id: int
) -> Optional[IntegrationWebhook]:
    """Get a webhook by endpoint ID and organization"""
    return db.query(IntegrationWebhook).filter(
        and_(
            IntegrationWebhook.endpoint_id == endpoint_id,
            IntegrationWebhook.organization_id == organization_id
        )
    ).first()


def get_webhooks(
    db: Session,
    organization_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[IntegrationWebhook]:
    """Get all webhooks for an organization"""
    return db.query(IntegrationWebhook).filter(
        IntegrationWebhook.organization_id == organization_id
    ).offset(skip).limit(limit).all()


def create_webhook(
    db: Session,
    webhook_in: WebhookCreate,
    organization_id: int
) -> IntegrationWebhook:
    """Create a new webhook"""
    webhook = IntegrationWebhook(
        id=str(uuid.uuid4()),
        organization_id=organization_id,
        endpoint_id=webhook_in.endpoint_id,
        name=webhook_in.name,
        url=webhook_in.url,
        event_types=[event.value for event in webhook_in.event_types],
        description=webhook_in.description,
        status="active",
        retry_config=webhook_in.retry_config.model_dump() if webhook_in.retry_config else {
            "max_retries": 3,
            "retry_delay": 60,
            "backoff_multiplier": 2.0
        }
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    logger.info(f"Created webhook {webhook_in.endpoint_id} for organization {organization_id}")
    return webhook


# ===== EVENT OPERATIONS =====

def create_event(
    db: Session,
    event_in: EventCreate,
    organization_id: int
) -> IntegrationEvent:
    """Create a new integration event for billing tracking"""
    event = IntegrationEvent(
        id=str(uuid.uuid4()),
        organization_id=organization_id,
        source_type=event_in.source_type,
        source_id=event_in.source_id,
        event_type=event_in.event_type,
        raw_data=event_in.raw_data,
        processed_data=event_in.processed_data or {},
        agent_id=event_in.agent_id
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    logger.info(f"Created event {event_in.event_type} from {event_in.source_id} for organization {organization_id}")
    return event


def get_events(
    db: Session,
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    source_type: Optional[str] = None,
    event_type: Optional[str] = None,
    agent_id: Optional[int] = None
) -> List[IntegrationEvent]:
    """Get integration events with optional filtering"""
    query = db.query(IntegrationEvent).filter(
        IntegrationEvent.organization_id == organization_id
    )
    
    if source_type:
        query = query.filter(IntegrationEvent.source_type == source_type)
    if event_type:
        query = query.filter(IntegrationEvent.event_type == event_type)
    if agent_id:
        query = query.filter(IntegrationEvent.agent_id == agent_id)
    
    return query.order_by(IntegrationEvent.created_at.desc()).offset(skip).limit(limit).all()


# ===== STREAM OPERATIONS =====

def get_stream(
    db: Session,
    stream_id: str,
    organization_id: int
) -> Optional[IntegrationStream]:
    """Get a stream by ID and organization"""
    return db.query(IntegrationStream).filter(
        and_(
            IntegrationStream.stream_id == stream_id,
            IntegrationStream.organization_id == organization_id
        )
    ).first()


def get_streams(
    db: Session,
    organization_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[IntegrationStream]:
    """Get all streams for an organization"""
    return db.query(IntegrationStream).filter(
        IntegrationStream.organization_id == organization_id
    ).offset(skip).limit(limit).all()


def create_stream(
    db: Session,
    stream_in: StreamCreate,
    organization_id: int
) -> IntegrationStream:
    """Create a new stream consumer"""
    stream = IntegrationStream(
        id=str(uuid.uuid4()),
        organization_id=organization_id,
        stream_id=stream_in.stream_id,
        name=stream_in.name,
        source_config=stream_in.source_config,
        processing_config=stream_in.processing_config or {},
        description=stream_in.description,
        status="active"
    )
    
    db.add(stream)
    db.commit()
    db.refresh(stream)
    
    logger.info(f"Created stream {stream_in.stream_id} for organization {organization_id}")
    return stream


# ===== UTILITY FUNCTIONS =====

def get_organization_integration_stats(
    db: Session,
    organization_id: int
) -> Dict[str, Any]:
    """Get integration statistics for an organization"""
    connectors_count = db.query(IntegrationConnector).filter(
        IntegrationConnector.organization_id == organization_id
    ).count()
    
    active_connectors_count = db.query(IntegrationConnector).filter(
        and_(
            IntegrationConnector.organization_id == organization_id,
            IntegrationConnector.status == "active"
        )
    ).count()
    
    webhooks_count = db.query(IntegrationWebhook).filter(
        IntegrationWebhook.organization_id == organization_id
    ).count()
    
    events_count = db.query(IntegrationEvent).filter(
        IntegrationEvent.organization_id == organization_id
    ).count()
    
    streams_count = db.query(IntegrationStream).filter(
        IntegrationStream.organization_id == organization_id
    ).count()
    
    return {
        "connectors": {
            "total": connectors_count,
            "active": active_connectors_count,
            "inactive": connectors_count - active_connectors_count
        },
        "webhooks": {
            "total": webhooks_count
        },
        "events": {
            "total": events_count
        },
        "streams": {
            "total": streams_count
        }
    }
