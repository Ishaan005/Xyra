"""
Integration layer configuration and settings.
"""
from pydantic_settings import BaseSettings

class IntegrationSettings(BaseSettings):
    """Settings for integration layer components"""
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_WEBHOOKS: str = "1000/minute"
    RATE_LIMIT_API: str = "500/minute"
    
    # Webhook Configuration
    WEBHOOK_MAX_PAYLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_ATTEMPTS: int = 3
    WEBHOOK_RETRY_DELAYS: str = "60,300,900"  # 1min, 5min, 15min
    
    # Batch Import Configuration
    BATCH_IMPORT_MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    BATCH_IMPORT_CHUNK_SIZE: int = 1000
    BATCH_IMPORT_UPLOAD_DIR: str = "/tmp/xyra_imports"
    BATCH_IMPORT_RETENTION_DAYS: int = 30
    
    # Streaming Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID_PREFIX: str = "xyra"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    STREAM_CONSUMER_TIMEOUT: int = 1000
    STREAM_METRICS_INTERVAL: int = 60
    
    # Connector Configuration
    CONNECTOR_DEFAULT_TIMEOUT: int = 30
    CONNECTOR_MAX_RETRIES: int = 3
    CONNECTOR_HEALTH_CHECK_INTERVAL: int = 300  # 5 minutes
    CONNECTOR_MAX_CONNECTIONS: int = 100
    
    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60
    
    # Monitoring and Logging
    ENABLE_METRICS_COLLECTION: bool = True
    METRICS_RETENTION_DAYS: int = 30
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_prefix = "INTEGRATION_"

# Integration settings instance
integration_settings = IntegrationSettings()

# Default configurations for different integration types
DEFAULT_WEBHOOK_CONFIG = {
    "retry_config": {
        "max_attempts": integration_settings.WEBHOOK_RETRY_ATTEMPTS,
        "retry_delays": [int(x) for x in integration_settings.WEBHOOK_RETRY_DELAYS.split(",")]
    },
    "timeout": integration_settings.WEBHOOK_TIMEOUT,
    "max_payload_size": integration_settings.WEBHOOK_MAX_PAYLOAD_SIZE
}

DEFAULT_STREAM_CONFIG = {
    "kafka": {
        "bootstrap_servers": [integration_settings.KAFKA_BOOTSTRAP_SERVERS],
        "group_id_prefix": integration_settings.KAFKA_GROUP_ID_PREFIX,
        "auto_offset_reset": "latest",
        "enable_auto_commit": True,
        "consumer_timeout": integration_settings.STREAM_CONSUMER_TIMEOUT
    },
    "redis": {
        "host": integration_settings.REDIS_HOST,
        "port": integration_settings.REDIS_PORT,
        "db": integration_settings.REDIS_DB
    }
}

DEFAULT_CONNECTOR_CONFIG = {
    "timeout": integration_settings.CONNECTOR_DEFAULT_TIMEOUT,
    "max_retries": integration_settings.CONNECTOR_MAX_RETRIES,
    "verify_ssl": True,
    "connect_timeout": 10,
    "headers": {
        "User-Agent": "Xyra-Integration/1.0"
    }
}

DEFAULT_BATCH_IMPORT_CONFIG = {
    "chunk_size": integration_settings.BATCH_IMPORT_CHUNK_SIZE,
    "max_file_size": integration_settings.BATCH_IMPORT_MAX_FILE_SIZE,
    "upload_directory": integration_settings.BATCH_IMPORT_UPLOAD_DIR,
    "retention_days": integration_settings.BATCH_IMPORT_RETENTION_DAYS,
    "supported_formats": ["csv", "json", "xml", "parquet", "excel"]
}
