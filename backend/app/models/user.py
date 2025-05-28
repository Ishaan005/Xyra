from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class User(BaseModel):
    """
    User model for authentication and organization management
    """
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    
    # New fields from revised schema
    last_login = Column(DateTime(timezone=True), nullable=True)
    role = Column(String(50), nullable=False, default='user')
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    
    def __str__(self) -> str:
        return f"User(email={self.email}, organization_id={self.organization_id})"