from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import time
import logging

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with connection pooling for better performance
# Following Azure best practices for database connection management
if not settings.SQLALCHEMY_DATABASE_URI:
    raise ValueError("SQLALCHEMY_DATABASE_URI is not configured")

logger.info(f"Creating database engine for: {settings.POSTGRES_SERVER}")
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Verify connections before usage to avoid stale connections
    pool_size=10,        # Number of connections to maintain in the pool
    max_overflow=20,     # Max number of connections above pool_size
    pool_timeout=30,     # Seconds to wait before timing out on getting a connection
    pool_recycle=1800,   # Recycle connections after 30 minutes to avoid stale connections
    echo=True if logger.level == logging.DEBUG else False  # Log SQL queries in debug mode
    # Local PostgreSQL doesn't require SSL
)

# Add connection event handlers for debugging
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    logger.info("Database connection established")

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checked out from pool")

@event.listens_for(engine, "checkin") 
def checkin(dbapi_connection, connection_record):
    logger.debug("Database connection checked back into pool")

# Create session factory with optimized settings
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Dependency function to get a database session and ensure proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def session_scope():
    """
    Context manager for database sessions with automatic error handling and cleanup.
    Provides automatic rollback on exceptions and automatic closing of the session.
    
    Example usage:
        with session_scope() as session:
            user = session.query(User).filter(User.id == user_id).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

# Add query execution time logging for debugging and performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.5:  # Log slow queries (taking more than 500ms)
        logger.warning(f"Slow query detected: {total:.2f}s - {statement}")