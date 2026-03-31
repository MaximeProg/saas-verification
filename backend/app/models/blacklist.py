from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.base import Base


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    type = Column(String(50), nullable=False, index=True)
    value = Column(String(255), nullable=False, index=True)
    
    reason = Column(Text)
    added_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
