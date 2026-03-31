from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.base import Base


class VerificationDuplicate(Base):
    __tablename__ = "verification_duplicates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    document_number = Column(String(100), index=True)
    email = Column(String(255), index=True)
    
    verification_count = Column(Integer, default=1)
    last_verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id"))
    
    is_flagged = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
