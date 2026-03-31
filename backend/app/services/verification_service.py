from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.models.verification import Verification
from app.models.company import Company
from app.core.security import generate_session_token
from app.config import settings


class VerificationService:
    """Service de gestion des vérifications KYC"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_verification(
        self,
        company_id: UUID,
        full_name: str,
        email: str,
        external_reference: str,
        phone: Optional[str] = None,
        country: Optional[str] = None,
        verification_type: str = "document"
    ) -> Verification:
        """Crée une nouvelle vérification"""
        
        # Générer ID unique
        count_result = await self.db.execute(
            select(func.count(Verification.id))
        )
        count = count_result.scalar() or 0
        verification_id = f"KYC-{datetime.utcnow().year}{count + 1:06d}"
        
        # Générer token de session
        session_token = generate_session_token()
        session_url = f"{settings.VERIFICATION_URL_BASE}/{session_token}"
        session_expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        
        # Créer vérification
        verification = Verification(
            verification_id=verification_id,
            company_id=company_id,
            full_name=full_name,
            email=email,
            phone=phone,
            country=country,
            external_reference=external_reference,
            verification_type=verification_type,
            session_token=session_token,
            session_url=session_url,
            session_expires_at=session_expires_at,
            status="pending"
        )
        
        self.db.add(verification)
        await self.db.commit()
        await self.db.refresh(verification)
        
        return verification
    
    async def get_verification_by_id(self, verification_id: str) -> Optional[Verification]:
        """Récupère une vérification par son ID"""
        result = await self.db.execute(
            select(Verification).where(Verification.verification_id == verification_id)
        )
        return result.scalar_one_or_none()
    
    async def get_verification_by_token(self, session_token: str) -> Optional[Verification]:
        """Récupère une vérification par son token de session"""
        result = await self.db.execute(
            select(Verification).where(Verification.session_token == session_token)
        )
        return result.scalar_one_or_none()
    
    async def list_verifications(
        self,
        company_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Verification], int]:
        """Liste les vérifications avec pagination"""
        
        query = select(Verification)
        
        if company_id:
            query = query.where(Verification.company_id == company_id)
        
        if status:
            query = query.where(Verification.status == status)
        
        # Compter le total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Récupérer les résultats paginés
        query = query.order_by(Verification.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        verifications = result.scalars().all()
        
        return list(verifications), total
    
    async def increment_quota(self, company_id: UUID):
        """Incrémente le quota utilisé d'une entreprise"""
        await self.db.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(quota_used=Company.quota_used + 1)
        )
        await self.db.commit()
    
    async def update_verification_status(
        self,
        verification_id: str,
        status: str,
        reviewed_by: Optional[UUID] = None,
        rejection_reason: Optional[str] = None
    ):
        """Met à jour le statut d'une vérification"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if reviewed_by:
            update_data["reviewed_by"] = reviewed_by
            update_data["reviewed_at"] = datetime.utcnow()
        
        if rejection_reason:
            update_data["rejection_reason"] = rejection_reason
        
        if status in ["approved", "rejected"]:
            update_data["completed_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(Verification)
            .where(Verification.verification_id == verification_id)
            .values(**update_data)
        )
        await self.db.commit()
