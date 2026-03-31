from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.payment import PaymentStatus, PaymentMethod


class PaymentBase(BaseModel):
    """Schéma de base pour un paiement"""
    plan_id: UUID
    payment_method: PaymentMethod
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = Field(None, max_length=20)
    callback_url: Optional[str] = Field(None, max_length=500)
    return_url: Optional[str] = Field(None, max_length=500)


class PaymentCreate(PaymentBase):
    """Schéma pour créer un paiement"""
    pass


class PaymentResponse(BaseModel):
    """Schéma de réponse pour un paiement"""
    id: UUID
    payment_reference: str
    company_id: UUID
    plan_id: UUID
    amount: float
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    fedapay_transaction_id: Optional[str] = None
    fedapay_token: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaymentInitResponse(BaseModel):
    """Réponse après initialisation d'un paiement"""
    payment_id: UUID
    payment_reference: str
    amount: float
    currency: str
    payment_url: str  # URL FedaPay pour effectuer le paiement
    token: Optional[str] = None  # Token FedaPay (peut être None)
    expires_at: datetime
    status: PaymentStatus


class PaymentCallbackData(BaseModel):
    """Données reçues du callback FedaPay"""
    transaction_id: str
    status: str
    amount: float
    currency: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    metadata: Optional[dict] = None


class PaymentStatusUpdate(BaseModel):
    """Mise à jour du statut d'un paiement"""
    status: PaymentStatus
    fedapay_status: Optional[str] = None
    fedapay_response: Optional[str] = None
    paid_at: Optional[datetime] = None


class PaymentListResponse(BaseModel):
    """Liste de paiements avec pagination"""
    total: int
    page: int
    page_size: int
    payments: list[PaymentResponse]
