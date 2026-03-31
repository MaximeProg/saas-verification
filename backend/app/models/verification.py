from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(String(50), unique=True, nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations utilisateur
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50))
    country = Column(String(100))
    external_reference = Column(String(255))
    
    # Type et statut
    verification_type = Column(String(50))
    status = Column(String(50), default="pending", index=True)
    
    # Session
    session_token = Column(String(255), unique=True)
    session_url = Column(Text)
    session_expires_at = Column(DateTime)
    
    # Document
    document_type = Column(String(50))
    document_number = Column(String(100), index=True)
    document_front_url = Column(Text)
    document_back_url = Column(Text)
    selfie_url = Column(Text)
    
    # Validation
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    reviewed_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Sécurité et tracking
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(JSONB)
    country_detected = Column(String(100))
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relations
    company = relationship("Company", back_populates="verifications")
    reviewer = relationship("AdminUser", foreign_keys=[reviewed_by])
    webhook_logs = relationship("WebhookLog", back_populates="verification", cascade="all, delete-orphan")
