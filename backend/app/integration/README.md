# Integration Layer Implementation

This document describes the implementation of the integration layer for the Xyra platform, providing comprehensive data collection capabilities for outcome measurement and attribution.

## Overview

The integration layer consists of five main components:

1. **Enhanced API Gateway** - Unified entry point with rate limiting, monitoring, and circuit breakers
2. **Webhook Receivers** - Real-time data collection from external systems
3. **Batch Importers** - Processing large volumes of historical/periodic data
4. **Streaming Consumers** - Real-time data stream processing
5. **Custom Connectors** - Specialized integrations for specific systems

## Components

### 1. Enhanced API Gateway

**Location**: `app/integration/api_gateway/`

**Features**:
- Rate limiting with configurable limits
- Request/response monitoring and metrics
- Circuit breaker pattern for resilience
- Health check endpoints
- API versioning support

**Endpoints**:
- `GET /health` - Health check with rate limiting
- `GET /metrics` - API metrics and performance data

**Usage**:
```python
from app.integration.api_gateway import setup_api_gateway

app = setup_api_gateway(app)
```

### 2. Webhook Receivers

**Location**: `app/integration/webhooks/`

**Features**:
- Webhook endpoint registration and management
- Signature verification (SHA256, SHA1)
- Automatic retry mechanisms with configurable delays
- Payload validation
- Dead letter queue for failed deliveries
- Rate limiting and abuse prevention

**Endpoints**:
- `POST /integration/webhooks/register` - Register new webhook endpoint
- `POST /integration/webhooks/{endpoint_id}` - Receive webhook payload
- `GET /integration/webhooks/{endpoint_id}/status` - Get webhook status
- `DELETE /integration/webhooks/{endpoint_id}` - Deactivate webhook
- `POST /integration/webhooks/test/{endpoint_id}` - Test webhook endpoint

**Example Registration**:
```json
{
  "endpoint_id": "stripe_webhooks",
  "url": "https://api.example.com/webhooks/stripe",
  "secret": "whsec_...",
  "events": ["payment.completed", "subscription.created"],
  "retry_config": {
    "max_attempts": 3,
    "retry_delays": [60, 300, 900]
  }
}
```

### 3. Batch Importers

**Location**: `app/integration/batch_importers/`

**Features**:
- Support for multiple file formats (CSV, JSON, XML, Parquet, Excel)
- Scheduled and one-time import jobs
- Data transformation and validation
- Incremental import with checkpointing
- Resumable imports for large datasets
- Progress monitoring and error reporting

**Endpoints**:
- `POST /integration/import/upload` - Upload file for processing
- `POST /integration/import/jobs` - Create import job
- `GET /integration/import/jobs` - List import jobs
- `GET /integration/import/jobs/{job_id}` - Get job status
- `POST /integration/import/jobs/{job_id}/retry` - Retry failed job
- `DELETE /integration/import/jobs/{job_id}` - Cancel job

**Example Job Creation**:
```json
{
  "name": "Customer Data Import",
  "job_type": "one_time",
  "data_format": "csv",
  "source_config": {
    "file_path": "/path/to/customers.csv",
    "chunk_size": 1000
  },
  "transformation_rules": {
    "column_mapping": {
      "customer_id": "id",
      "customer_name": "name"
    },
    "data_types": {
      "id": "int64",
      "created_at": "datetime"
    }
  }
}
```

### 4. Streaming Consumers

**Location**: `app/integration/streaming/`

**Features**:
- Support for Kafka, Redis Streams, and WebSocket
- Real-time message processing
- Automatic scaling and partitioning
- Dead letter queue for failed messages
- Consumer lag monitoring
- Throughput metrics

**Endpoints**:
- `POST /integration/streams` - Create stream processor
- `POST /integration/streams/{stream_id}/start` - Start stream
- `POST /integration/streams/{stream_id}/stop` - Stop stream
- `POST /integration/streams/{stream_id}/pause` - Pause stream
- `POST /integration/streams/{stream_id}/resume` - Resume stream
- `GET /integration/streams/{stream_id}/metrics` - Get stream metrics
- `GET /integration/streams` - List all streams
- `WebSocket /integration/streams/{stream_id}/ws` - WebSocket endpoint

**Example Stream Creation**:
```json
{
  "stream_id": "agent_events",
  "protocol": "kafka",
  "config": {
    "topics": ["agent.interactions", "agent.outcomes"],
    "bootstrap_servers": ["localhost:9092"],
    "group_id": "xyra_processors",
    "auto_offset_reset": "latest"
  }
}
```

### 5. Custom Connectors

**Location**: `app/integration/connectors/`

**Features**:
- REST API and GraphQL connectors
- Flexible authentication (API Key, Bearer Token, Basic Auth, OAuth2)
- Connection health monitoring
- Automatic retry logic
- Custom data extraction and transformation
- Performance metrics and monitoring

**Endpoints**:
- `POST /integration/connectors` - Create connector
- `GET /integration/connectors` - List connectors
- `GET /integration/connectors/{connector_id}` - Get connector details
- `POST /integration/connectors/{connector_id}/test` - Test connection
- `POST /integration/connectors/{connector_id}/extract` - Extract data
- `DELETE /integration/connectors/{connector_id}` - Delete connector

**Example Connector Creation**:
```json
{
  "connector_id": "salesforce_api",
  "name": "Salesforce CRM Integration",
  "connector_type": "rest_api",
  "config": {
    "base_url": "https://your-instance.salesforce.com",
    "auth": {
      "type": "bearer_token",
      "token": "your_access_token"
    },
    "timeout": 30,
    "verify_ssl": true
  }
}
```

## Configuration

Integration layer settings are managed in `app/integration/config.py`:

```python
from app.integration.config import integration_settings

# Rate limiting
RATE_LIMIT_DEFAULT = "100/minute"
WEBHOOK_MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Streaming
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
REDIS_HOST = "localhost"

# Batch processing
BATCH_IMPORT_CHUNK_SIZE = 1000
BATCH_IMPORT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
```

## Installation and Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Environment Variables**:
```bash
# Integration layer settings
INTEGRATION_KAFKA_BOOTSTRAP_SERVERS=localhost:9092
INTEGRATION_REDIS_HOST=localhost
INTEGRATION_BATCH_IMPORT_UPLOAD_DIR=/tmp/xyra_imports
```

3. **Start the Application**:
```bash
python main.py
```

## Monitoring and Health Checks

### Health Endpoints
- `GET /health` - Overall system health
- `GET /metrics` - System metrics and performance data

### Monitoring Features
- Request/response metrics for all endpoints
- Stream processing lag and throughput
- Connector health and performance
- Import job progress and error rates
- Circuit breaker status and failure rates

### Metrics Collected
- Total requests and response times
- Success/failure rates
- Data processing volumes
- System resource usage
- Error rates and types

## Error Handling and Resilience

### Circuit Breaker Pattern
- Automatic failure detection
- Service isolation during outages
- Gradual recovery testing

### Retry Mechanisms
- Exponential backoff for failed requests
- Dead letter queues for permanent failures
- Configurable retry policies

### Monitoring and Alerting
- Real-time health monitoring
- Automatic error detection
- Performance degradation alerts

## Security Considerations

### Authentication
- Support for multiple auth methods
- Secure credential storage
- Token refresh mechanisms

### Data Protection
- SSL/TLS for all external connections
- Payload signature verification
- Rate limiting and abuse prevention

### Access Control
- API key validation
- Role-based access control
- Audit logging

## Examples and Use Cases

### Real-time AI Agent Data Collection
```python
# Create Kafka stream for agent interactions
stream_config = {
    "stream_id": "agent_interactions",
    "protocol": "kafka",
    "config": {
        "topics": ["agent.chat", "agent.completion"],
        "bootstrap_servers": ["localhost:9092"]
    }
}
```

### Batch Customer Data Import
```python
# Import customer data from CSV
import_config = {
    "name": "Monthly Customer Import",
    "job_type": "scheduled",
    "data_format": "csv",
    "schedule_config": {
        "frequency": "monthly",
        "day": 1,
        "time": "02:00"
    }
}
```

### CRM Integration
```python
# Connect to Salesforce API
connector_config = {
    "connector_id": "salesforce",
    "name": "Salesforce CRM",
    "connector_type": "rest_api",
    "config": {
        "base_url": "https://your-instance.salesforce.com",
        "auth": {"type": "oauth2"}
    }
}
```

This integration layer provides a comprehensive foundation for collecting and processing data from various sources to enable outcome-based pricing and measurement.
