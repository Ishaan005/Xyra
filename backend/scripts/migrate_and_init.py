#!/usr/bin/env python3
"""
Database migration and initialization script for Xyra backend.
This script handles both Alembic migrations and fallback table creation.
"""
import sys
import os
import logging
import time
from pathlib import Path
from urllib.parse import quote_plus

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Import settings and db after adding to path
from app.core.config import settings
from app.db.session import Base, engine

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
            
            test_engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
            with test_engine.connect() as conn:
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

def check_alembic_available():
    """Check if Alembic is properly configured"""
    try:
        alembic_cfg_path = backend_dir / "alembic.ini"
        if not alembic_cfg_path.exists():
            logger.warning(f"Alembic configuration not found: {alembic_cfg_path}")
            return False
        
        versions_dir = backend_dir / "alembic" / "versions"
        if not versions_dir.exists():
            logger.warning(f"Alembic versions directory not found: {versions_dir}")
            return False
            
        return True
    except Exception as e:
        logger.warning(f"Alembic configuration check failed: {e}")
        return False

def get_current_revision():
    """Get current database revision"""
    try:
        test_engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        with test_engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()
    except Exception as e:
        logger.warning(f"Could not determine current revision: {e}")
        return None

def run_alembic_migrations():
    """
    Run Alembic database migrations.
    """
    try:
        # Set up Alembic configuration
        alembic_cfg_path = backend_dir / "alembic.ini"
        alembic_cfg = Config(str(alembic_cfg_path))
        
        # Override the sqlalchemy.url in alembic config with our settings
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))
        
        logger.info("Starting Alembic database migrations...")
        
        # Check current revision
        current_rev = get_current_revision()
        logger.info(f"Current database revision: {current_rev}")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic database migrations completed successfully!")
        
        # Check final revision
        final_rev = get_current_revision()
        logger.info(f"Final database revision: {final_rev}")
        
        return True
        
    except Exception as e:
        logger.error(f"Alembic migration failed: {str(e)}")
        return False

def run_direct_table_creation():
    """
    Fallback: Create tables directly using SQLAlchemy metadata.
    This is used when Alembic migrations fail or are not available.
    """
    try:
        logger.info("Running direct table creation as fallback...")
        logger.info("Creating database tables using SQLAlchemy metadata...")
        
        # Import all models to ensure they're registered with Base.metadata
        from app.models.user import User
        from app.models.organization import Organization
        from app.models.agent import Agent, AgentActivity, AgentCost, AgentOutcome
        from app.models.billing_model import (
            BillingModel, AgentBasedConfig, ActivityBasedConfig, OutcomeBasedConfig,
            WorkflowBasedConfig, WorkflowType, CommitmentTier,
            OutcomeMetric, OutcomeVerificationRule
        )
        from app.models.invoice import Invoice, InvoiceLineItem
        from app.models.api_key import ApiKey
        
        # Log the number of tables that will be created
        table_names = [table.name for table in Base.metadata.tables.values()]
        logger.info(f"Total tables to create: {len(table_names)}")
        logger.info(f"Table names: {', '.join(sorted(table_names))}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Direct table creation completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Direct table creation failed: {str(e)}")
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
                logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists.")
            else:
                logger.info(f"Creating initial superuser: {settings.FIRST_SUPERUSER}")
                # Create a UserCreate instance with the necessary data
                user_in = UserCreate(
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    full_name="Initial Admin",
                    is_superuser=True,
                    is_active=True,
                    organization_id=None  # Set to None or an actual organization ID if needed
                )
                # Create user using the UserCreate instance
                create_user(db=db, user_in=user_in)
                logger.info(f"Superuser {settings.FIRST_SUPERUSER} created successfully.")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create initial superuser: {str(e)}")
        return False

def main():
    """
    Main migration and initialization function.
    Strategy:
    1. Wait for database connection
    2. Try Alembic migrations first (preferred)
    3. Fallback to direct table creation if Alembic fails
    4. Create initial superuser
    """
    logger.info("=== XYRA DATABASE MIGRATION SCRIPT ===")
    logger.info("Starting database migration and initialization...")
    
    # Step 1: Wait for database
    logger.info("Step 1: Waiting for database connection...")
    if not wait_for_database():
        logger.error("Database connection failed")
        sys.exit(1)
    
    # Step 2: Try Alembic migrations
    logger.info("Step 2: Attempting Alembic migrations...")
    migration_success = False
    
    if check_alembic_available():
        migration_success = run_alembic_migrations()
    else:
        logger.warning("Alembic not available, skipping to direct table creation")
    
    # Step 3: Fallback to direct table creation if needed
    if not migration_success:
        logger.info("Step 3: Running fallback direct table creation...")
        if not run_direct_table_creation():
            logger.error("Both Alembic migrations and direct table creation failed")
            sys.exit(1)
    else:
        logger.info("Step 3: Skipping direct table creation (Alembic succeeded)")
    
    # Step 4: Create initial superuser
    logger.info("Step 4: Creating initial superuser...")
    if not create_initial_superuser():
        logger.warning("Initial superuser creation failed, but continuing...")
    
    logger.info("=== DATABASE MIGRATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
