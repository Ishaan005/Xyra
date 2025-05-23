import os
import secrets
from typing import List, Optional, Any, Union
import urllib.parse

from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Xyra"
    
    # Secret key for token generation
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # JWT settings
    ALGORITHM: str = "HS256"  # Standard algorithm for JWT tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Origins (allow local dev frontend)
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database configuration
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_OPTIONS: str = os.getenv("POSTGRES_OPTIONS", "?sslmode=require")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        
        # For Azure PostgreSQL, use proper URL encoding for credentials
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_SERVER")
        db = values.get("POSTGRES_DB", "")
        options = values.get("POSTGRES_OPTIONS", "?sslmode=require")
        
        # Ensure all components are present
        if not all([user, password, host]):
            raise ValueError("Missing required database connection parameters")
        
        # Properly URL encode each credential component separately
        user_encoded = urllib.parse.quote_plus(user)
        password_encoded = urllib.parse.quote_plus(password)
        
        # Build connection string with properly encoded components
        conn_str = f"postgresql://{user_encoded}:{password_encoded}@{host}:5432/{db}{options}"
        return conn_str
    
    # Stripe API key
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET")
      # Frontend URL for callbacks
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() in ("true", "1", "t")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@example.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "Xyra")
    
    # Enhanced email settings for enterprise features
    DKIM_PRIVATE_KEY: Optional[str] = os.getenv("DKIM_PRIVATE_KEY")
    DKIM_SELECTOR: Optional[str] = os.getenv("DKIM_SELECTOR", "default")
    EMAIL_QUEUE_MAX_WORKERS: int = int(os.getenv("EMAIL_QUEUE_MAX_WORKERS", "2"))
    EMAIL_BATCH_SIZE: int = int(os.getenv("EMAIL_BATCH_SIZE", "20"))
    EMAIL_MAX_RETRIES: int = int(os.getenv("EMAIL_MAX_RETRIES", "3"))
    EMAIL_RETRY_DELAY: int = int(os.getenv("EMAIL_RETRY_DELAY", "1"))
    EMAIL_STATUS_RETENTION_DAYS: int = int(os.getenv("EMAIL_STATUS_RETENTION_DAYS", "30"))
    EMAIL_TRACKING_ENABLED: bool = os.getenv("EMAIL_TRACKING_ENABLED", "True").lower() in ("true", "1", "t")
    EMAIL_RATE_LIMIT: int = int(os.getenv("EMAIL_RATE_LIMIT", "100"))  # Emails per hour
    
    # Authentication settings for Azure
    AZURE_TENANT_ID: Optional[str] = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    AZURE_KEY_VAULT_URL: Optional[str] = os.getenv("AZURE_KEY_VAULT_URL")
    
    # Default admin user
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()