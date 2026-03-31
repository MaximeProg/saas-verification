from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    
    endpoint = Column(String(255), index=True)
    method = Column(String(10))
    status_code = Column(Integer)
    
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    request_body = Column(JSONB)
    response_body = Column(JSONB)
    
    execution_time_ms = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relations
    company = relationship("Company", back_populates="api_logs")


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id", ondelete="CASCADE"), index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    
    event_type = Column(String(100))
    webhook_url = Column(Text)
    
    payload = Column(JSONB)
    response_status = Column(Integer)
    response_body = Column(Text)
    
    retry_count = Column(Integer, default=0)
    success = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    verification = relationship("Verification", back_populates="webhook_logs")
    company = relationship("Company", back_populates="webhook_logs")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_email = Column(String(255), index=True)
    recipient_type = Column(String(50))
    
    subject = Column(String(500))
    template_name = Column(String(100))
    
    status = Column(String(50), index=True)
    error_message = Column(Text)
    
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
