from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional, Annotated

from app.db.session import get_db
from app.schemas.admin import AdminCreate, AdminLogin, AdminResponse, TokenResponse
from app.schemas.company import CompanyDetail
from app.schemas.verification import VerificationDetail, VerificationList
from app.models.admin import AdminUser
from app.models.company import Company
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_admin
)
from app.services.verification_service import VerificationService

router = APIRouter()


@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(
    data: AdminCreate,
    db: AsyncSession = Depends(get_db)
):
    """Créer un nouvel administrateur (premier admin uniquement)"""
    
    # Vérifier si un admin existe déjà
    result = await db.execute(select(AdminUser))
    existing_admins = result.scalars().all()
    
    if len(existing_admins) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Création d'admin désactivée. Utilisez un admin existant."
        )
    
    # Vérifier si username existe
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur existe déjà"
        )
    
    # Créer admin
    admin = AdminUser(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=data.role
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    return admin


@router.post("/login", response_model=TokenResponse)
async def login_admin(
    data: AdminLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login administrateur"""
    
    # Chercher admin
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == data.username)
    )
    admin = result.scalar_one_or_none()
    
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte administrateur désactivé"
        )
    
    # Mettre à jour last_login
    admin.last_login = datetime.utcnow()
    await db.commit()
    
    # Créer token JWT
    access_token = create_access_token(
        data={"sub": str(admin.id), "type": "admin", "role": admin.role}
    )
    
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    admin: AdminUser = Depends(get_current_admin)
):
    """Récupère les informations de l'admin connecté"""
    return admin


@router.get("/companies", response_model=list[CompanyDetail])
async def list_companies(
    status_filter: Annotated[Optional[str], Query()] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Liste toutes les entreprises (admin uniquement)"""
    
    query = select(Company)
    
    if status_filter:
        query = query.where(Company.status == status_filter)
    
    query = query.order_by(Company.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return list(companies)


@router.post("/companies/{company_id}/validate-documents", response_model=CompanyDetail)
async def validate_company_documents(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Valider les documents d'entreprise (RCCM, registre de commerce, etc.)"""
    
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    if not company.documents_submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'entreprise n'a pas encore soumis ses documents"
        )
    
    # Valider les documents
    company.documents_validated = True
    company.documents_validated_at = datetime.utcnow()
    company.documents_rejection_reason = None
    company.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(company)
    
    # TODO: Envoyer email de confirmation à l'entreprise
    
    return company


@router.post("/companies/{company_id}/reject-documents", response_model=CompanyDetail)
async def reject_company_documents(
    company_id: str,
    reason: str,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Rejeter les documents d'entreprise avec une raison"""
    
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    if not company.documents_submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'entreprise n'a pas encore soumis ses documents"
        )
    
    # Rejeter les documents
    company.documents_validated = False
    company.documents_submitted = False  # Doit resoumettre
    company.documents_rejection_reason = reason
    company.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(company)
    
    # TODO: Envoyer email avec raison du rejet
    
    return company


@router.post("/companies/{company_id}/validate", response_model=CompanyDetail)
async def validate_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Valider une entreprise et passer en mode production"""
    
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entreprise non trouvée"
        )
    
    # Mettre à jour statut
    company.is_validated = True
    company.validated_at = datetime.utcnow()
    company.validated_by = admin.id
    company.status = "production"
    company.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(company)
    
    # TODO: Envoyer email de confirmation à l'entreprise
    
    return company


@router.get("/verifications", response_model=VerificationList)
async def list_all_verifications(
    status_filter: Annotated[Optional[str], Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Liste toutes les vérifications (admin uniquement)"""
    
    if page < 1:
        page = 1
    if page_size > 100:
        page_size = 100
    
    skip = (page - 1) * page_size
    
    service = VerificationService(db)
    verifications, total = await service.list_verifications(
        status=status_filter,
        skip=skip,
        limit=page_size
    )
    
    return VerificationList(
        total=total,
        page=page,
        page_size=page_size,
        verifications=verifications
    )
