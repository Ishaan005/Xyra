import os
import secrets
from typing import List, Optional, Dict, Any, Union
import urllib.parse

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Xyra"
    
    # Secret key for token generation
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Token expiration time in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Origins
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
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
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    
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


settings = Settings()