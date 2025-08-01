#!/usr/bin/env python3
"""
Database migration script for Xyra backend.
This script runs Alembic migrations safely and handles Azure-specific configurations.
"""

import logging
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Import settings after adding to path
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_database(max_retries=30, retry_delay=2):
    """
    Wait for database to become available.
    Following Azure best practices for database connectivity:
    - Retry logic with exponential backoff
    - Proper error handling for different connection issues
    """
    attempts = 0
    
    # Check if database URL is configured
    if not settings.SQLALCHEMY_DATABASE_URI:
        logger.error("Database URL not configured")
        return False
    
    # Sanitize connection string for logging
    db_url_sanitized = str(settings.SQLALCHEMY_DATABASE_URI)
    if settings.POSTGRES_PASSWORD:
        db_url_sanitized = db_url_sanitized.replace(
            quote_plus(settings.POSTGRES_PASSWORD), "********"
        )
    
    logger.info("Waiting for database connection...")
    logger.info(f"Server: {settings.POSTGRES_SERVER}")
    logger.info(f"Database: {settings.POSTGRES_DB}")
    logger.info(f"Username: {settings.POSTGRES_USER}")
    
    while attempts < max_retries:
        try:
            attempts += 1
            logger.info(f"Database connection attempt {attempts}/{max_retries}")
            
            engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1;"))
                result.scalar()
                logger.info("Database connection successful!")
                return True
                
        except OperationalError as e:
            error_str = str(e).lower()
            if "password authentication failed" in error_str:
                logger.error("Authentication failed. Check database credentials.")
                return False
            elif "no pg_hba.conf entry" in error_str:
                logger.error("Firewall rule missing. Add your IP to Azure PostgreSQL firewall.")
                return False
            elif "could not translate host name" in error_str:
                logger.error("Hostname resolution error. Check connection string format.")
                return False
            elif attempts < max_retries:
                delay = retry_delay * (2 ** (attempts - 1))
                logger.warning(f"Database not ready: {str(e)}")
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to connect after {max_retries} attempts: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Unexpected database error: {str(e)}")
            return False
    
    logger.error("Database connection timeout")
    return False

def run_migrations():
    """
    Run Alembic database migrations.
    """
    try:
        # Check if database URL is configured
        if not settings.SQLALCHEMY_DATABASE_URI:
            logger.error("Database URL not configured")
            return False
            
        # Set up Alembic configuration
        alembic_cfg_path = backend_dir / "alembic.ini"
        if not alembic_cfg_path.exists():
            logger.error(f"Alembic configuration not found: {alembic_cfg_path}")
            return False
            
        alembic_cfg = Config(str(alembic_cfg_path))
        
        # Override the sqlalchemy.url in alembic config with our settings
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))
        
        logger.info("Starting database migrations...")
        
        # Check current revision
        try:
            from alembic.runtime.migration import MigrationContext
            
            engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
            with engine.connect() as conn:
                context = MigrationContext.configure(conn)
                current_rev = context.get_current_revision()
                logger.info(f"Current database revision: {current_rev}")
        except Exception as e:
            logger.warning(f"Could not determine current revision: {e}")
            current_rev = None
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully!")
        
        # Check final revision
        try:
            from alembic.runtime.migration import MigrationContext
            
            engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
            with engine.connect() as conn:
                context = MigrationContext.configure(conn)
                final_rev = context.get_current_revision()
                logger.info(f"Final database revision: {final_rev}")
        except Exception as e:
            logger.warning(f"Could not determine final revision: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def create_initial_superuser():
    """
    Create initial superuser if specified in environment variables.
    """
    if not (settings.FIRST_SUPERUSER and settings.FIRST_SUPERUSER_PASSWORD):
        logger.info("No initial superuser configuration found, skipping user creation")
        return True
    
    try:
        from app.db.session import session_scope
        from app.models.user import User
        from app.services.user_service import create_user
        from app.schemas.user import UserCreate
        
        with session_scope() as db:
            # Check if superuser already exists
            existing_user = db.query(User).filter(
                User.email == settings.FIRST_SUPERUSER
            ).first()
            
            if existing_user:
                logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists")
                return True
            
            logger.info(f"Creating initial superuser: {settings.FIRST_SUPERUSER}")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Initial Admin",
                is_superuser=True,
                is_active=True,
                organization_id=None
            )
            create_user(db=db, user_in=user_in)
            logger.info("Initial superuser created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to create initial superuser: {str(e)}")
        return False

def main():
    """
    Main migration function.
    """
    logger.info("=== Starting Xyra Database Migration Process ===")
    
    # Step 1: Wait for database to be available
    if not wait_for_database():
        logger.error("Database connection failed")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_migrations():
        logger.error("Database migrations failed")
        sys.exit(1)
    
    # Step 3: Create initial superuser
    if not create_initial_superuser():
        logger.error("Initial superuser creation failed")
        sys.exit(1)
    
    logger.info("=== Database Migration Process Completed Successfully ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
