from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Schema for JWT token responses"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for JWT token payload"""
    sub: Optional[str] = None
    exp: Optional[int] = None