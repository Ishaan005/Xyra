from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class ApiKey(BaseModel):
    """
    API Key model for programmatic access to the Xyra API
    """
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)  # Owner of the API key
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)  # Organization the key belongs to
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)  # Hashed version of the key
    key_prefix = Column(String(20), nullable=False)  # First few chars for display
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
    
    # Optional metadata
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string for future permission system
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    organization = relationship("Organization", back_populates="api_keys")
    
    def __str__(self) -> str:
        return f"ApiKey(name={self.name}, user_id={self.user_id}, org_id={self.organization_id}, active={self.is_active})"
