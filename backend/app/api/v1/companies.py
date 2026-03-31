from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional, Annotated

from app.db.session import get_db
from app.schemas.company import CompanyCreate, CompanyLogin, CompanyResponse, CompanyDetail, APIKeyResponse, CompanyBusinessDocuments, WebhookUpdate
from app.schemas.admin import TokenResponse
from app.models.company import Company
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_api_keys,
    generate_webhook_secret,
    verify_api_key,
    get_current_company_from_jwt
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Inscription d'une nouvelle entreprise
    Statut initial: sandbox (mode test)
    L'entreprise peut se connecter immédiatement et soumettre ses documents business plus tard
    """
    
    # Vérifier si email existe déjà
    result = await db.execute(
        select(Company).where(Company.email == data.email)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette adresse email est déjà utilisée"
        )
    
    # Générer clés API
    public_key, secret_key = generate_api_keys()
    webhook_secret = generate_webhook_secret()
    
    # Hash du mot de passe (pour login dashboard)
    password_hash = get_password_hash(data.password)
    
    # Créer entreprise avec plan gratuit de 5 vérifications
    company = Company(
        company_name=data.company_name,
        email=data.email,
        password_hash=password_hash,
        phone=data.phone,
        country=data.country,
        address=data.address,
        rccm=data.rccm,
        tax_number=data.tax_number,
        website=data.website,
        legal_representative=data.legal_representative,
        status="sandbox",
        is_validated=False,
        documents_submitted=False,
        documents_validated=False,
        subscription_plan="free",
        monthly_quota=5,
        quota_used=0,
        public_key=public_key,
        secret_key=secret_key,
        webhook_secret=webhook_secret
    )
    
    db.add(company)
    await db.commit()
    await db.refresh(company)
    
    # Créer token JWT pour connexion automatique
    access_token = create_access_token(
        data={"sub": str(company.id), "type": "company"}
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login_company(
    data: CompanyLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login entreprise pour accéder au dashboard"""
    
    # Chercher entreprise
    result = await db.execute(
        select(Company).where(Company.email == data.email)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Vérifier mot de passe
    if not verify_password(data.password, company.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Créer token JWT
    access_token = create_access_token(
        data={"sub": str(company.id), "type": "company"}
    )
    
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=CompanyDetail)
async def get_current_company(
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """Récupère les informations de l'entreprise connectée via JWT token"""
    return company


@router.get("/api-keys", response_model=APIKeyResponse)
async def get_api_keys(
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """Récupère les clés API de l'entreprise (authentification JWT)"""
    
    return APIKeyResponse(
        public_key=company.public_key,
        secret_key=company.secret_key
    )


@router.post("/api-keys/regenerate", response_model=APIKeyResponse)
async def regenerate_api_keys(
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """Régénère les clés API de l'entreprise (authentification JWT)"""
    
    # Vérifier que le compte est en production
    if company.status != "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La régénération des clés API n'est disponible que pour les comptes en mode production"
        )
    
    # Vérifier que l'abonnement est actif
    if company.subscription_expires_at and company.subscription_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre abonnement a expiré. Veuillez renouveler votre abonnement pour régénérer vos clés API"
        )
    
    # Générer nouvelles clés
    public_key, secret_key = generate_api_keys()
    
    company.public_key = public_key
    company.secret_key = secret_key
    company.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(company)
    
    return APIKeyResponse(
        public_key=public_key,
        secret_key=secret_key,
        message="Nouvelles clés générées. Mettez à jour votre intégration."
    )


@router.post("/submit-business-documents", response_model=CompanyDetail)
async def submit_business_documents(
    data: CompanyBusinessDocuments,
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """
    Soumettre les documents business après inscription (authentification JWT)
    Permet de passer du mode test au mode production après validation admin
    """
    
    # Mettre à jour les informations business
    company.phone = data.phone
    company.address = data.address
    company.rccm = data.rccm
    company.tax_number = data.tax_number
    company.legal_representative = data.legal_representative
    company.website = data.website
    company.documents_submitted = True
    company.documents_validated = False  # En attente de validation admin
    company.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(company)
    
    # TODO: Notifier l'admin pour validation
    
    return company


@router.put("/webhook", response_model=CompanyDetail)
async def update_webhook(
    data: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """
    Mettre à jour l'URL webhook de l'entreprise (authentification JWT)
    """
    
    company.webhook_url = data.webhook_url
    company.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(company)
    
    return company


