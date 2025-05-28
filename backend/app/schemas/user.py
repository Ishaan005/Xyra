from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    role: str = 'user'  # New field from revised schema


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    organization_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    organization_id: Optional[int] = None
    role: Optional[str] = None


class UserInDBBase(UserBase):
    """Base schema for users in DB, includes ID"""
    id: int
    organization_id: Optional[int] = None
    last_login: Optional[datetime] = None  # New field from revised schema
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True for Pydantic v2 compatibility


class User(UserInDBBase):
    """Schema for user responses"""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in DB with hashed password"""
    hashed_password: str