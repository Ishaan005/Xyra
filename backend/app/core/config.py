import os
import secrets
from typing import List, Optional, Any, Union
import urllib.parse

from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
import os
# Load .env from the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Xyra"
    
    # Secret key for token generation
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # JWT settings
    ALGORITHM: str = "HS256"  # Standard algorithm for JWT tokens
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Origins (allow local dev frontend)
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database configuration
    POSTGRES_SERVER: Optional[str] = os.getenv("POSTGRES_SERVER")
    POSTGRES_USER: Optional[str] = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: Optional[str] = os.getenv("POSTGRES_DB")
    POSTGRES_OPTIONS: str = os.getenv("POSTGRES_OPTIONS", "")
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
        db = values.get("POSTGRES_DB")
        options = values.get("POSTGRES_OPTIONS", "")
        
        # Ensure all components are present
        if not all([user, password, host]):
            raise ValueError("Missing required database connection parameters")
        
        # Properly URL encode each credential component separately
        user_encoded = urllib.parse.quote_plus(str(user))
        password_encoded = urllib.parse.quote_plus(str(password))
        
        # Build connection string with properly encoded components
        conn_str = f"postgresql://{user_encoded}:{password_encoded}@{host}:5432/{db}{options}"
        return conn_str
    
    # Stripe API key
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Authentication settings for Azure
    AZURE_TENANT_ID: Optional[str] = os.getenv("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    AZURE_KEY_VAULT_URL: Optional[str] = os.getenv("AZURE_KEY_VAULT_URL")
    
    # Default admin user
    FIRST_SUPERUSER: Optional[str] = os.getenv("FIRST_SUPERUSER")
    FIRST_SUPERUSER_PASSWORD: Optional[str] = os.getenv("FIRST_SUPERUSER_PASSWORD")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()