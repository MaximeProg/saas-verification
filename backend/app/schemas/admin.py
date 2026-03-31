from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AdminCreate(BaseModel):
    """Création d'un administrateur"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Optional[str] = Field(default="admin", description="super_admin, admin, reviewer")


class AdminLogin(BaseModel):
    """Login admin"""
    username: str
    password: str


class AdminResponse(BaseModel):
    """Réponse admin"""
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Réponse token JWT"""
    access_token: str
    token_type: str = "bearer"
