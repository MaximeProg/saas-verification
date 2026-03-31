from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import datetime
import base64

from app.db.session import get_db
from app.services.verification_service import VerificationService
from app.schemas.verification import VerificationDetail
from app.tasks.image_tasks import process_verification_documents

router = APIRouter()


@router.get("/{session_token}", response_model=VerificationDetail)
async def get_verification_by_session(
    session_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère une vérification par son token de session
    Utilisé par la page de vérification utilisateur
    """
    
    service = VerificationService(db)
    verification = await service.get_verification_by_token(session_token)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session de vérification non trouvée"
        )
    
    # Vérifier expiration
    if verification.session_expires_at and verification.session_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Cette session de vérification a expiré"
        )
    
    return verification


@router.post("/{session_token}/submit-documents")
async def submit_documents(
    session_token: str,
    document_type: Annotated[str, Form()],
    document_number: Annotated[str, Form()],
    document_front: Annotated[UploadFile, File()],
    document_back: Annotated[UploadFile, File()] = None,
    selfie: Annotated[UploadFile, File()] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Soumission des documents par l'utilisateur
    
    Workflow:
    1. Validation session token
    2. Sauvegarde temporaire des fichiers
    3. Réponse immédiate
    4. Background: compression + upload Cloudinary
    """
    
    service = VerificationService(db)
    verification = await service.get_verification_by_token(session_token)
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session de vérification non trouvée"
        )
    
    # Vérifier expiration
    if verification.session_expires_at and verification.session_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Cette session de vérification a expiré"
        )
    
    # Vérifier que pas déjà soumis
    if verification.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Documents déjà soumis"
        )
    
    # Valider types de fichiers
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    if document_front.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de fichier non supporté pour le recto"
        )
    
    if document_back and document_back.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de fichier non supporté pour le verso"
        )
    
    if selfie and selfie.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de fichier non supporté pour le selfie"
        )
    
    # Lire les fichiers
    front_data = await document_front.read()
    back_data = await document_back.read() if document_back else None
    selfie_data = await selfie.read() if selfie else None
    
    # Mettre à jour les infos de base
    verification.document_type = document_type
    verification.document_number = document_number
    verification.status = "in_review"
    verification.updated_at = datetime.utcnow()
    
    await db.commit()
    
    # Lancer les tasks Celery en background
    # Encoder les images en base64 pour Celery
    front_b64 = base64.b64encode(front_data).decode('utf-8')
    back_b64 = base64.b64encode(back_data).decode('utf-8') if back_data else None
    selfie_b64 = base64.b64encode(selfie_data).decode('utf-8') if selfie_data else None
    
    # Lancer le traitement asynchrone
    task = process_verification_documents.delay(
        verification_id=verification.verification_id,
        front_data_base64=front_b64,
        back_data_base64=back_b64,
        selfie_data_base64=selfie_b64
    )
    
    return {
        "success": True,
        "message": "Documents soumis avec succès",
        "verification_id": verification.verification_id,
        "status": verification.status
    }
