from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import schemas
from app.models.user import User
from app.core.config import settings
from app.core.security import verify_password
from app.db.session import SessionLocal

# Create OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


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
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
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


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency function to get the current active user.
    Ensures the user is active.
    """
    if not current_user.is_active:
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
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def get_current_admin_or_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency function to get the current admin or superuser.
    Ensures the user is either an admin or a superuser.
    """
    if not (current_user.is_superuser or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def authenticate_user(
    db: Session, username: str, password: str
) -> Optional[User]:
    """
    Authenticate a user by username and password.
    """
    # Try to find user with the given username
    user = db.query(User).filter(User.username == username).first()
    
    # If user exists, verify password
    if user and verify_password(password, user.hashed_password):
        return user
    
    # Authentication failed
    return None