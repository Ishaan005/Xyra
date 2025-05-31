import logging
import time
from urllib.parse import quote_plus
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy import text
import sys

from app.db.session import Base, engine
from app.models.user import User
from app.models.organization import Organization
from app.models.agent import Agent, AgentActivity, AgentCost, AgentOutcome
from app.models.billing_model import BillingModel
from app.models.invoice import Invoice, InvoiceLineItem
from app.core.config import settings
from app.services.user_service import create_user
from app.db.session import session_scope
from app.schemas.user import UserCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(max_retries=5, retry_delay=3) -> None:
    """
    Initialize the database with all tables defined in the models.
    Following Azure best practices for database operations:
    - Using parameterized schema definition through SQLAlchemy ORM
    - Retry logic with exponential backoff for transient failures
    - Proper error handling and logging
    - Idempotent operations (safe to run multiple times)
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Initial delay between retries in seconds (doubles after each retry)
    """
    attempts = 0
    
    # Sanitize connection string for logging
    db_url_sanitized = str(settings.SQLALCHEMY_DATABASE_URI)
    if settings.POSTGRES_PASSWORD:
        db_url_sanitized = db_url_sanitized.replace(
            quote_plus(settings.POSTGRES_PASSWORD), "********"
        )
    
    logger.info("Using Azure PostgreSQL connection settings:")
    logger.info(f"Server: {settings.POSTGRES_SERVER}")
    logger.info(f"Database: {settings.POSTGRES_DB}")
    logger.info(f"Username: {settings.POSTGRES_USER}")
    logger.info(f"SSL Mode: {settings.POSTGRES_OPTIONS}")
    
    while attempts < max_retries:
        try:
            attempts += 1
            logger.info(f"Creating database tables (attempt {attempts}/{max_retries})...")
            logger.info(f"Connecting to database: {db_url_sanitized}")
            
            # Test connection first - using SQLAlchemy 2.0+ syntax with text()
            with engine.connect() as conn:
                logger.info("Successfully connected to database!")
                logger.info("Running query to verify connection...")
                # Use text() to create a proper executable SQL statement
                result = conn.execute(text("SELECT version();"))
                version = result.scalar()
                logger.info(f"Connected to: {version}")
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully!")
            
            # Create initial superuser if specified in environment variables
            if settings.FIRST_SUPERUSER and settings.FIRST_SUPERUSER_PASSWORD:
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
            
            return
        except OperationalError as e:
            error_str = str(e).lower()
            if "password authentication failed" in error_str:
                logger.error("Authentication failed. Please check your database credentials.")
                logger.error(f"Error details: {str(e)}")
                logger.error("For Azure PostgreSQL, ensure you're using the correct username format:")
                if settings.POSTGRES_SERVER:
                    logger.error(f"  - Try using: username@{settings.POSTGRES_SERVER.split('.')[0]}")
                else:
                    logger.error("  - Try using: username@servername")
                logger.error("  - Example: xyraadmin@xyrasql")
                break
            elif "no pg_hba.conf entry" in error_str:
                logger.error(f"Firewall rule missing: {str(e)}")
                logger.error(f"Please add your IP address to the Azure PostgreSQL firewall rules")
                logger.error(f"In Azure Portal: PostgreSQL server > Security > Networking > Add client IP")
                break
            elif "could not translate host name" in error_str:
                logger.error(f"Hostname resolution error: {str(e)}")
                logger.error("There's a problem with the connection string format.")
                logger.error("Check the .env file and ensure special characters are properly escaped")
                break
            elif "does not exist" in error_str and "database" in error_str:
                logger.error(f"Database '{settings.POSTGRES_DB}' does not exist.")
                logger.error(f"Please create the database in Azure PostgreSQL first.")
                break
            elif attempts < max_retries:
                delay = retry_delay * (2 ** (attempts - 1))
                logger.warning(f"Database connection failed: {str(e)}")
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts.")
                logger.error(f"Error details: {str(e)}")
                raise
        except ProgrammingError as e:
            if "database" in str(e) and "does not exist" in str(e):
                logger.error(f"Database doesn't exist: {str(e)}")
                logger.error("Please create the database in Azure PostgreSQL first.")
            else:
                logger.error(f"Database programming error: {str(e)}")
            break
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            logger.error(f"Unexpected error: {type(e).__name__}")
            raise

if __name__ == "__main__":
    logger.info("Creating initial database tables...")
    try:
        init_db()
        logger.info("Database initialization completed.")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)