from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import schemas
from app.models.user import User
from app.core.config import settings
from app.core.security import verify_password
from app.db.session import SessionLocal
from app.services import api_key_service

# Create OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False  # Don't automatically error if no token
)

# Create HTTPBearer scheme for API key authentication
api_key_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    """
    Dependency function to get a database session.
    Creates a new database session for each request and closes it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency function to get the current user based on the JWT token.
    """
    try:
        # Decode JWT token using settings.ALGORITHM
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_user_from_api_key(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(api_key_scheme)
) -> User:
    """
    Dependency function to get the current user based on API key.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    if not api_key.startswith("xyra_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key_obj = api_key_service.authenticate_api_key(db, api_key)
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == api_key_obj.user_id).first()
    if not user or not getattr(user, 'is_active', False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_user_flexible(
    db: Session = Depends(get_db),
    jwt_token: Optional[str] = Depends(oauth2_scheme),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(api_key_scheme)
) -> User:
    """
    Dependency that accepts either JWT or API key authentication.
    """
    # Try JWT authentication first
    if jwt_token:
        try:
            payload = jwt.decode(
                jwt_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            token_data = schemas.TokenPayload(**payload)
            user = db.query(User).filter(User.id == token_data.sub).first()
            if user and getattr(user, 'is_active', False):
                return user
        except (InvalidTokenError, ValidationError):
            pass  # Fall through to API key authentication
    
    # Try API key authentication
    if credentials and credentials.credentials:
        api_key = credentials.credentials
        if api_key.startswith("xyra_"):
            api_key_obj = api_key_service.authenticate_api_key(db, api_key)
            if api_key_obj:
                user = db.query(User).filter(User.id == api_key_obj.user_id).first()
                if user and getattr(user, 'is_active', False):
                    return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency function to get the current active user.
    Ensures the user is active.
    """
    if current_user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency function to get the current superuser.
    Ensures the user is a superuser.
    """
    if current_user.is_superuser is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def get_current_admin_or_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency function to get the current superuser.
    Ensures the user is a superuser.
    Note: This function is equivalent to get_current_superuser since there's no is_admin field.
    """
    if not bool(current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def authenticate_user(
    db: Session, email: str, password: str
) -> Optional[User]:
    """
    Authenticate a user by email and password.
    """
    # Try to find user with the given email
    user = db.query(User).filter(User.email == email).first()
    
    # If user exists, verify password
    if user and verify_password(password, str(user.hashed_password)):
        return user
    
    # Authentication failed
    return None