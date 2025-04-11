from typing import Optional
import logging
from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app import schemas

# Configure logging
logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email
    """
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID
    """
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Get multiple users with pagination
    """
    return db.query(User).offset(skip).limit(limit).all()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password
    """
    try:
        user = get_user_by_email(db, email=email)
        if not user:
            logger.warning(f"Authentication failed: User not found with email {email}")
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for user {email}")
            return None
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user
    """
    # Check if user already exists
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise ValueError(f"User with email {user_in.email} already exists")
    
    # Create user with hashed password
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
        organization_id=user_in.organization_id,
    )
    
    # Add user to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Created new user: {user.email}")
    return user


def update_user(db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """
    Update a user
    """
    user = get_user(db, user_id=user_id)
    if not user:
        logger.warning(f"User update failed: User not found with ID {user_id}")
        return None
    
    # Update user properties - Using model_dump instead of dict for Pydantic v2
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Handle password update separately to hash it
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Update user attributes
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    # Commit changes to database
    db.commit()
    db.refresh(user)
    
    logger.info(f"Updated user: {user.email}")
    return user


def delete_user(db: Session, user_id: int) -> Optional[User]:
    """
    Delete a user
    """
    user = get_user(db, user_id=user_id)
    if not user:
        logger.warning(f"User deletion failed: User not found with ID {user_id}")
        return None
    
    # Delete user from database
    db.delete(user)
    db.commit()
    
    logger.info(f"Deleted user: {user.email}")
    return user


# For FastAPI dependency
def get_current_user(db: Session, token: str) -> Optional[User]:
    """
    Get current user from JWT token
    This is implemented in app/api/deps.py
    """
    pass


def get_current_active_user(current_user: User) -> User:
    """
    Get current active user
    This is implemented in app/api/deps.py
    """
    if not current_user.is_active:
        raise ValueError("Inactive user")
    return current_user