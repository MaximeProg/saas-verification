from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Annotated
from fastapi import Query

from app.db.session import get_db
from app.schemas.verification import (
    VerificationInitiate,
    VerificationResponse,
    VerificationDetail,
    VerificationList,
    VerificationReview
)
from app.services.verification_service import VerificationService
from app.core.security import verify_api_key, get_current_admin, get_current_company_from_jwt
from app.models.company import Company
from app.models.admin import AdminUser
from app.tasks.email_tasks import send_verification_initiated_email
from app.tasks.webhook_tasks import send_verification_status_change
from sqlalchemy import select, func
from app.models.verification import Verification
from fastapi import UploadFile, File, Form
from app.core.storage import upload_file
from datetime import datetime

router = APIRouter()


@router.post("/initiate", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def initiate_verification(
    data: VerificationInitiate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(verify_api_key)
):
    """
    Initier une nouvelle vérification KYC
    
    Workflow:
    1. Vérification que l'entreprise est validée
    2. Vérification qu'elle a un abonnement actif
    3. Validation quota entreprise
    4. Création vérification en DB (status: pending)
    5. Génération session token unique
    6. Réponse immédiate avec URL
    7. Background: email notification
    """
    
    # Vérifier que les documents de l'entreprise sont soumis ET validés
    if not company.documents_submitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez soumettre vos documents d'entreprise (RCCM, registre de commerce, etc.) avant de pouvoir initier des vérifications"
        )
    
    if not company.documents_validated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vos documents d'entreprise sont en cours de validation par notre équipe. Vous pourrez initier des vérifications une fois validés."
        )
    
    # Vérifier qu'elle a un abonnement (plan gratuit inclus)
    if not company.subscription_plan:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez avoir un plan d'abonnement pour initier des vérifications"
        )
    
    service = VerificationService(db)
    
    # Vérifier quota
    if company.monthly_quota and company.quota_used >= company.monthly_quota:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quota mensuel atteint"
        )
    
    # Créer vérification (rapide, juste insertion DB)
    verification = await service.create_verification(
        company_id=company.id,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        country=data.country,
        external_reference=data.external_reference,
        verification_type=data.verification_type
    )
    
    # Incrémenter quota
    await service.increment_quota(company.id)
    
    # Envoyer email en background (Celery) - optionnel
    try:
        send_verification_initiated_email.delay(
            recipient_email=data.email,
            recipient_name=data.full_name,
            verification_id=verification.verification_id,
            verification_url=verification.session_url
        )
    except Exception as e:
        # Celery non disponible - continuer sans email
        print(f"Email non envoyé (Celery indisponible): {e}")
    
    # Réponse immédiate
    return VerificationResponse(
        verification_id=verification.verification_id,
        verification_url=verification.session_url,
        status=verification.status
    )


@router.get("/stats")
async def get_verification_stats(
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """Récupère les statistiques des vérifications pour l'entreprise connectée"""
    
    # Compter le total de vérifications
    total_result = await db.execute(
        select(func.count(Verification.id)).where(Verification.company_id == company.id)
    )
    total_verifications = total_result.scalar() or 0
    
    # Compter par statut
    pending_result = await db.execute(
        select(func.count(Verification.id)).where(
            Verification.company_id == company.id,
            Verification.status == "pending"
        )
    )
    pending = pending_result.scalar() or 0
    
    verified_result = await db.execute(
        select(func.count(Verification.id)).where(
            Verification.company_id == company.id,
            Verification.status == "approved"
        )
    )
    verified = verified_result.scalar() or 0
    
    rejected_result = await db.execute(
        select(func.count(Verification.id)).where(
            Verification.company_id == company.id,
            Verification.status == "rejected"
        )
    )
    rejected = rejected_result.scalar() or 0
    
    return {
        "total_verifications": total_verifications,
        "pending": pending,
        "verified": verified,
        "rejected": rejected
    }


@router.get("/{verification_id}", response_model=VerificationDetail)
async def get_verification(
    verification_id: str,
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """Récupère les détails d'une vérification"""
    
    service = VerificationService(db)
    verification = await service.get_verification_by_id(verification_id)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vérification non trouvée"
        )
    
    # Vérifier que la vérification appartient à l'entreprise
    if verification.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    
    return verification


@router.get("/", response_model=VerificationList)
async def list_verifications(
    status_filter: Annotated[Optional[str], Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    db: AsyncSession = Depends(get_db),
    company: Company = Depends(get_current_company_from_jwt)
):
    """Liste les vérifications de l'entreprise avec pagination (authentification JWT)"""
    
    if page < 1:
        page = 1
    if page_size > 100:
        page_size = 100
    
    skip = (page - 1) * page_size
    
    service = VerificationService(db)
    verifications, total = await service.list_verifications(
        company_id=company.id,
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


@router.post("/{verification_id}/review", response_model=VerificationDetail)
async def review_verification(
    verification_id: str,
    review: VerificationReview,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    Validation admin d'une vérification (approve/reject)
    Endpoint réservé aux administrateurs
    """
    
    service = VerificationService(db)
    verification = await service.get_verification_by_id(verification_id)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vérification non trouvée"
        )
    
    if verification.status not in ["pending", "in_review"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette vérification ne peut plus être modifiée"
        )
    
    # Valider action
    if review.action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action invalide. Utilisez 'approve' ou 'reject'"
        )
    
    # Mettre à jour statut
    old_status = verification.status
    new_status = "approved" if review.action == "approve" else "rejected"
    await service.update_verification_status(
        verification_id=verification_id,
        status=new_status,
        reviewed_by=admin.id,
        rejection_reason=review.rejection_reason if review.action == "reject" else None
    )
    
    # Envoyer webhook en background
    send_verification_status_change.delay(
        verification_id=verification_id,
        old_status=old_status,
        new_status=new_status,
        company_id=str(verification.company_id)
    )
    
    # Récupérer vérification mise à jour
    verification = await service.get_verification_by_id(verification_id)
    
    return verification


@router.get("/session/{session_token}")
async def get_verification_by_session(
    session_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère une vérification par son token de session
    Endpoint public pour la page de soumission utilisateur
    """
    service = VerificationService(db)
    verification = await service.get_verification_by_token(session_token)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lien de vérification invalide"
        )
    
    # Vérifier expiration
    if verification.session_expires_at and verification.session_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Ce lien de vérification a expiré"
        )
    
    return {
        "verification_id": verification.verification_id,
        "full_name": verification.full_name,
        "email": verification.email,
        "status": verification.status,
        "session_expires_at": verification.session_expires_at
    }


@router.post("/session/{session_token}/submit")
async def submit_verification_documents(
    session_token: str,
    document_front: UploadFile = File(...),
    selfie: UploadFile = File(...),
    document_type: str = Form(...),
    document_number: str = Form(...),
    document_back: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Soumission des documents par l'utilisateur
    Endpoint public accessible via le lien de vérification
    """
    service = VerificationService(db)
    verification = await service.get_verification_by_token(session_token)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lien de vérification invalide"
        )
    
    # Vérifier expiration
    if verification.session_expires_at and verification.session_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Ce lien de vérification a expiré"
        )
    
    # Vérifier statut
    if verification.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette vérification a déjà été soumise"
        )
    
    # Upload des fichiers
    try:
        front_url = await upload_file(document_front, f"verifications/{verification.verification_id}")
        selfie_url = await upload_file(selfie, f"verifications/{verification.verification_id}")
        back_url = None
        if document_back:
            back_url = await upload_file(document_back, f"verifications/{verification.verification_id}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload des fichiers: {str(e)}"
        )
    
    # Mettre à jour la vérification
    verification.document_type = document_type
    verification.document_number = document_number
    verification.document_front_url = front_url
    verification.document_back_url = back_url
    verification.selfie_url = selfie_url
    verification.status = "in_review"
    verification.submitted_at = datetime.utcnow()
    verification.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(verification)
    
    # Envoyer webhook en background
    try:
        send_verification_status_change.delay(
            verification_id=verification.verification_id,
            old_status="pending",
            new_status="in_review",
            company_id=str(verification.company_id)
        )
    except Exception as e:
        print(f"Webhook non envoyé: {e}")
    
    return {
        "message": "Documents soumis avec succès",
        "verification_id": verification.verification_id,
        "status": verification.status
    }
