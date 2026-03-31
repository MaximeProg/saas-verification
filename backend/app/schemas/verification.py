from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class VerificationInitiate(BaseModel):
    """Schéma pour initier une vérification"""
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    country: Optional[str] = None
    external_reference: str = Field(..., description="Référence externe de l'entreprise")
    verification_type: Optional[str] = Field(default="document", description="document, database, full")


class VerificationResponse(BaseModel):
    """Réponse après initiation d'une vérification"""
    verification_id: str
    verification_url: str
    status: str
    
    class Config:
        from_attributes = True


class VerificationDetail(BaseModel):
    """Détails complets d'une vérification"""
    id: UUID
    verification_id: str
    company_id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    country: Optional[str]
    external_reference: str
    verification_type: Optional[str]
    status: str
    session_url: Optional[str]
    document_type: Optional[str]
    document_number: Optional[str]
    document_front_url: Optional[str]
    document_back_url: Optional[str]
    selfie_url: Optional[str]
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VerificationList(BaseModel):
    """Liste paginée de vérifications"""
    total: int
    page: int
    page_size: int
    verifications: list[VerificationDetail]


class VerificationSubmit(BaseModel):
    """Soumission des documents par l'utilisateur"""
    document_type: str = Field(..., description="passport, id_card, driver_license")
    document_number: str
    

class VerificationReview(BaseModel):
    """Validation admin d'une vérification"""
    action: str = Field(..., description="approve ou reject")
    rejection_reason: Optional[str] = None
