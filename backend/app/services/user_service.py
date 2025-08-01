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
        logger.info(f"Attempting to authenticate user: {email}")
        user = get_user_by_email(db, email=email)
        if not user:
            logger.warning(f"Authentication failed: User not found with email {email}")
            # Log all existing users for debugging (remove this in production)
            all_users = db.query(User).all()
            logger.info(f"Existing users in database: {[u.email for u in all_users]}")
            return None
        
        logger.info(f"User found: {user.email}, checking password")
        if not verify_password(password, str(user.hashed_password)):
            logger.warning(f"Authentication failed: Invalid password for user {email}")
            return None
        
        logger.info(f"Authentication successful for user: {email}")
        return user
    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}")
        return None


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user
    """
    # Check if user already exists
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise ValueError(f"User with email {user_in.email} already exists")
    
    organization_id = user_in.organization_id
    
    # If no organization_id provided, create a personal organization for the user
    if not organization_id:
        from app.services.organization_service import create_organization
        from app.schemas.organization import OrganizationCreate
        
        # Extract organization name from user's name or email
        if user_in.full_name and user_in.full_name.strip():
            org_name = f"{user_in.full_name.strip()}'s Organization"
        else:
            org_name = f"{user_in.email.split('@')[0]}'s Organization"
        
        try:
            # Create personal organization
            org_data = OrganizationCreate(
                name=org_name,
                description=f"Personal organization for {user_in.email}"
            )
            organization = create_organization(db, org_data)
            organization_id = organization.id
            logger.info(f"Created personal organization '{org_name}' for user {user_in.email}")
        except ValueError as e:
            # If organization name already exists, add timestamp or make it unique
            import time
            timestamp = int(time.time())
            org_name = f"{user_in.email.split('@')[0]} Organization {timestamp}"
            org_data = OrganizationCreate(
                name=org_name,
                description=f"Personal organization for {user_in.email}"
            )
            organization = create_organization(db, org_data)
            organization_id = organization.id
            logger.info(f"Created fallback organization '{org_name}' for user {user_in.email}")
    
    # Create user with hashed password
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
        organization_id=organization_id,
    )
    
    # Add user to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Created new user: {user.email} with organization_id: {organization_id}")
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
    if current_user.is_active is False:
        raise ValueError("Inactive user")
    return current_user