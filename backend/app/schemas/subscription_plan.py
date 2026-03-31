from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID


class SubscriptionPlanBase(BaseModel):
    """Schéma de base pour un plan d'abonnement"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)
    description: str
    price: float = Field(..., ge=0)
    currency: str = Field(default="XOF", max_length=3)
    billing_period: str = Field(default="monthly")
    monthly_quota: int = Field(..., ge=0)
    max_api_keys: int = Field(default=5, ge=1)
    max_users: int = Field(default=1, ge=1)
    features: Dict = Field(default_factory=dict)
    advantages: List[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    is_popular: bool = Field(default=False)
    is_custom: bool = Field(default=False)
    display_order: int = Field(default=0)


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schéma pour créer un plan d'abonnement"""
    pass


class SubscriptionPlanUpdate(BaseModel):
    """Schéma pour mettre à jour un plan d'abonnement"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    billing_period: Optional[str] = None
    monthly_quota: Optional[int] = Field(None, ge=0)
    max_api_keys: Optional[int] = Field(None, ge=1)
    max_users: Optional[int] = Field(None, ge=1)
    features: Optional[Dict] = None
    advantages: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_popular: Optional[bool] = None
    is_custom: Optional[bool] = None
    display_order: Optional[int] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Schéma de réponse pour un plan d'abonnement"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class SubscriptionPlanPublic(BaseModel):
    """Schéma public pour affichage des plans (sans infos sensibles)"""
    id: UUID
    name: str
    slug: str
    description: str
    price: float
    currency: str
    billing_period: str
    monthly_quota: int
    max_api_keys: int
    max_users: int
    advantages: List[str]
    is_popular: bool
    is_active: bool
    display_order: int
    features: List[str] = []
    
    # Fonctionnalités principales (filtrées)
    has_webhook_support: bool = False
    has_priority_support: bool = False
    has_custom_branding: bool = False
    has_api_access: bool = True
    has_bulk_upload: bool = False
    has_advanced_analytics: bool = False
    
    class Config:
        from_attributes = True
