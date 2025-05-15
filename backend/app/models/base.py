from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr

from app.db.session import Base

class BaseModel(Base):
    """
    Base class for all models with common functionality
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    @declared_attr
    def __tablename__(cls):
        """
        Generate table name automatically from class name
        """
        return cls.__name__.lower()