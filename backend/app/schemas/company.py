from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CompanyCreate(BaseModel):
    """Création d'une entreprise"""
    company_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    country: str = Field(..., description="Code pays ISO (ex: BJ, FR, US)")
    phone: Optional[str] = None
    address: Optional[str] = None
    rccm: Optional[str] = Field(None, description="Registre de commerce")
    tax_number: Optional[str] = Field(None, description="Numéro fiscal")
    website: Optional[str] = None
    legal_representative: Optional[str] = None


class CompanyLogin(BaseModel):
    """Login entreprise"""
    email: EmailStr
    password: str


class CompanyBusinessDocuments(BaseModel):
    """Soumission des documents business"""
    phone: str
    address: str
    rccm: str = Field(..., description="Registre de commerce")
    tax_number: str = Field(..., description="Numéro fiscal")
    legal_representative: str
    website: Optional[str] = None


class WebhookUpdate(BaseModel):
    """Mise à jour de l'URL webhook"""
    webhook_url: Optional[str] = None


class CompanyResponse(BaseModel):
    """Réponse entreprise"""
    id: UUID
    company_name: str
    email: str
    phone: Optional[str]
    country: Optional[str]
    status: str
    is_validated: bool
    subscription_plan: Optional[str]
    monthly_quota: Optional[int]
    quota_used: int
    public_key: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompanyDetail(BaseModel):
    """Détails complets entreprise"""
    id: UUID
    company_name: str
    email: str
    phone: Optional[str]
    country: Optional[str]
    address: Optional[str]
    rccm: Optional[str]
    tax_number: Optional[str]
    website: Optional[str]
    legal_representative: Optional[str]
    status: str
    is_validated: bool
    validated_at: Optional[datetime]
    documents_submitted: Optional[bool] = None
    documents_validated: Optional[bool] = None
    documents_validated_at: Optional[datetime] = None
    documents_rejection_reason: Optional[str] = None
    subscription_plan: Optional[str]
    monthly_quota: Optional[int]
    quota_used: int
    subscription_expires_at: Optional[datetime]
    public_key: Optional[str]
    secret_key: Optional[str]
    webhook_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyResponse(BaseModel):
    """Réponse avec clés API"""
    public_key: str
    secret_key: str
    message: str = "Conservez votre clé secrète en lieu sûr"
