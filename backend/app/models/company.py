from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50))
    country = Column(String(100))
    address = Column(Text)
    rccm = Column(String(100))
    tax_number = Column(String(100))
    website = Column(String(255))
    legal_representative = Column(String(255))
    
    # Statut et environnement
    status = Column(String(50), default="sandbox", index=True)
    is_validated = Column(Boolean, default=False)
    validated_at = Column(DateTime)
    validated_by = Column(UUID(as_uuid=True))
    
    # Documents de l'entreprise (KYB - Know Your Business)
    documents_submitted = Column(Boolean, default=False)
    documents_validated = Column(Boolean, default=False)
    documents_validated_at = Column(DateTime)
    documents_rejection_reason = Column(Text)
    
    # Abonnement
    subscription_plan_id = Column(UUID(as_uuid=True))
    subscription_plan = Column(String(50))
    monthly_quota = Column(Integer)
    quota_used = Column(Integer, default=0)
    subscription_started_at = Column(DateTime)
    subscription_expires_at = Column(DateTime)
    
    # Sécurité
    password_hash = Column(String(255), nullable=False)
    public_key = Column(String(255), unique=True, index=True)
    secret_key = Column(String(255), unique=True)
    webhook_url = Column(String(500))
    webhook_secret = Column(String(255))
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    verifications = relationship("Verification", back_populates="company", cascade="all, delete-orphan")
    api_logs = relationship("APILog", back_populates="company", cascade="all, delete-orphan")
    webhook_logs = relationship("WebhookLog", back_populates="company", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="company", cascade="all, delete-orphan")
