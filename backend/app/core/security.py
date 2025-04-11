from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token settings
ALGORITHM = "HS256"

# Create Azure Key Vault client if configured
key_vault_client = None
if settings.AZURE_KEY_VAULT_URL:
    try:
        # Use DefaultAzureCredential for secure authentication following Azure best practices
        credential = DefaultAzureCredential()
        key_vault_client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)
    except Exception as e:
        print(f"Failed to initialize Key Vault client: {e}")

def get_secret_key() -> str:
    """
    Get the secret key from Azure Key Vault if configured, otherwise use local setting.
    Following Azure best practices to avoid hardcoded credentials.
    """
    if key_vault_client:
        try:
            return key_vault_client.get_secret("jwt-secret-key").value
        except Exception:
            pass
    return settings.SECRET_KEY

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return encoded_jwt