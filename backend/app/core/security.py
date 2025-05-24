from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import logging

from jose import jwt
from passlib.context import CryptContext
import bcrypt  # Added for direct bcrypt usage if needed
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
            secret_value = key_vault_client.get_secret("jwt-secret-key").value
            if secret_value is not None:
                return secret_value
        except Exception:
            pass
    return settings.SECRET_KEY

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches hash, False otherwise
    """
    try:
        # Try using passlib's context first
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Passlib verify failed, trying direct bcrypt: {str(e)}")
        try:
            # Fall back to direct bcrypt if passlib has issues
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    try:
        # Try using passlib's context first
        return pwd_context.hash(password)
    except Exception as e:
        logger.warning(f"Passlib hash failed, trying direct bcrypt: {str(e)}")
        try:
            # Fall back to direct bcrypt if passlib has issues
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing error: {str(e)}")
            raise

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    Args:
        subject: Subject to encode in token (typically user ID)
        expires_delta: Optional expiration time
        
    Returns:
        Encoded JWT token as string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=settings.ALGORITHM)
    return encoded_jwt