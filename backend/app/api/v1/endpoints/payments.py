from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
import secrets

from app.db.session import get_db
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.subscription_plan import SubscriptionPlan
from app.models.company import Company
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentInitResponse,
    PaymentCallbackData,
    PaymentListResponse
)
from app.core.security import verify_api_key, get_current_company_from_jwt
from app.services.fedapay import fedapay_service

router = APIRouter()


def generate_payment_reference() -> str:
    """Génère une référence unique de paiement"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4).upper()
    return f"PAY-{timestamp}-{random_part}"


@router.post("/initialize", response_model=PaymentInitResponse)
async def initialize_payment(
    payment_data: PaymentCreate,
    current_company: Company = Depends(get_current_company_from_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialiser un paiement pour acheter un plan d'abonnement (authentification JWT)
    L'entreprise doit avoir ses documents validés avant de pouvoir acheter un plan
    """
    # Vérifier que l'entreprise a soumis et validé ses documents
    if not current_company.documents_submitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez soumettre vos documents d'entreprise avant de pouvoir acheter un plan d'abonnement"
        )
    
    if not current_company.documents_validated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vos documents d'entreprise doivent être validés par un administrateur avant de pouvoir acheter un plan d'abonnement"
        )
    
    # Vérifier que le plan existe
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == payment_data.plan_id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    if not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This subscription plan is not available"
        )
    
    # Créer le paiement en DB
    payment_reference = generate_payment_reference()
    
    new_payment = Payment(
        payment_reference=payment_reference,
        company_id=current_company.id,
        plan_id=plan.id,
        amount=plan.price,
        currency=plan.currency,
        payment_method=payment_data.payment_method,
        status=PaymentStatus.PENDING,
        customer_email=payment_data.customer_email or current_company.email,
        customer_phone=payment_data.customer_phone or current_company.phone,
        callback_url=payment_data.callback_url,
        return_url=payment_data.return_url,
        description=f"Abonnement {plan.name} - {plan.billing_period}",
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    
    # Créer la transaction FedaPay
    try:
        fedapay_result = fedapay_service.create_transaction(
            amount=plan.price,
            currency=plan.currency,
            description=new_payment.description,
            customer_email=new_payment.customer_email,
            customer_phone=new_payment.customer_phone,
            callback_url=payment_data.callback_url,
            metadata={
                "payment_id": str(new_payment.id),
                "payment_reference": payment_reference,
                "company_id": str(current_company.id),
                "plan_id": str(plan.id)
            }
        )
    except Exception as e:
        # Mettre à jour le paiement comme échoué
        await db.execute(
            update(Payment)
            .where(Payment.id == new_payment.id)
            .values(
                status=PaymentStatus.FAILED,
                fedapay_response=f"Exception: {str(e)}"
            )
        )
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create FedaPay transaction: {str(e)}"
        )
    
    if not fedapay_result.get("success"):
        # Mettre à jour le paiement comme échoué
        await db.execute(
            update(Payment)
            .where(Payment.id == new_payment.id)
            .values(
                status=PaymentStatus.FAILED,
                fedapay_response=str(fedapay_result.get("error"))
            )
        )
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize payment: {fedapay_result.get('error')}"
        )
    
    # Log pour debug
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"FedaPay result: {fedapay_result}")
    
    # Vérifier que payment_url existe
    payment_url = fedapay_result.get("payment_url")
    if not payment_url:
        await db.execute(
            update(Payment)
            .where(Payment.id == new_payment.id)
            .values(
                status=PaymentStatus.FAILED,
                fedapay_response="No payment_url in FedaPay response"
            )
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FedaPay did not return a payment URL. Response: {fedapay_result}"
        )
    
    # Mettre à jour le paiement avec les infos FedaPay
    transaction_id = fedapay_result.get("transaction_id")
    await db.execute(
        update(Payment)
        .where(Payment.id == new_payment.id)
        .values(
            fedapay_transaction_id=str(transaction_id) if transaction_id else None,
            fedapay_token=fedapay_result.get("token"),
            fedapay_status=fedapay_result.get("status"),
            status=PaymentStatus.PROCESSING
        )
    )
    await db.commit()
    
    return PaymentInitResponse(
        payment_id=new_payment.id,
        payment_reference=payment_reference,
        amount=plan.price,
        currency=plan.currency,
        payment_url=payment_url,
        token=fedapay_result.get("token"),
        expires_at=new_payment.expires_at,
        status=PaymentStatus.PROCESSING
    )


@router.post("/webhook")
async def fedapay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook FedaPay pour recevoir les notifications de paiement
    """
    # Récupérer le payload
    payload = await request.json()
    
    # TODO: Vérifier la signature du webhook
    signature = request.headers.get("X-FedaPay-Signature", "")
    
    # Traiter le webhook
    webhook_data = fedapay_service.process_webhook(payload, signature)
    
    transaction_id = webhook_data.get("transaction_id")
    status = webhook_data.get("status")
    metadata = webhook_data.get("metadata", {})
    
    # Récupérer le paiement
    payment_id = metadata.get("payment_id")
    
    if not payment_id:
        return {"status": "ignored", "reason": "No payment_id in metadata"}
    
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        return {"status": "error", "reason": "Payment not found"}
    
    # Mettre à jour le statut du paiement
    new_status = PaymentStatus.PENDING
    
    if status in ["approved", "completed"]:
        new_status = PaymentStatus.COMPLETED
        paid_at = datetime.utcnow()
        
        # Activer l'abonnement de l'entreprise
        result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == payment.plan_id)
        )
        plan = result.scalar_one_or_none()
        
        if plan:
            # Calculer la date d'expiration
            if plan.billing_period == "monthly":
                expires_at = datetime.utcnow() + timedelta(days=30)
            elif plan.billing_period == "yearly":
                expires_at = datetime.utcnow() + timedelta(days=365)
            else:
                expires_at = datetime.utcnow() + timedelta(days=30)
            
            # Mettre à jour l'entreprise
            await db.execute(
                update(Company)
                .where(Company.id == payment.company_id)
                .values(
                    subscription_plan_id=plan.id,
                    subscription_plan=plan.name,
                    monthly_quota=plan.monthly_quota,
                    quota_used=0,
                    subscription_started_at=datetime.utcnow(),
                    subscription_expires_at=expires_at
                )
            )
        
    elif status == "failed":
        new_status = PaymentStatus.FAILED
        paid_at = None
    elif status == "cancelled":
        new_status = PaymentStatus.CANCELLED
        paid_at = None
    else:
        paid_at = None
    
    # Mettre à jour le paiement
    await db.execute(
        update(Payment)
        .where(Payment.id == payment.id)
        .values(
            status=new_status,
            fedapay_status=status,
            fedapay_response=str(payload),
            paid_at=paid_at
        )
    )
    await db.commit()
    
    return {"status": "success", "payment_id": str(payment_id)}


@router.get("/my-payments", response_model=PaymentListResponse)
async def get_my_payments(
    page: int = 1,
    page_size: int = 20,
    current_company: Company = Depends(get_current_company_from_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer l'historique des paiements de l'entreprise (authentification JWT)
    """
    # Compter le total
    count_result = await db.execute(
        select(Payment).where(Payment.company_id == current_company.id)
    )
    total = len(count_result.scalars().all())
    
    # Récupérer les paiements paginés
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Payment)
        .where(Payment.company_id == current_company.id)
        .order_by(Payment.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    payments = result.scalars().all()
    
    return PaymentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        payments=payments
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_company: Company = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer les détails d'un paiement
    """
    result = await db.execute(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.company_id == current_company.id
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("/{payment_id}/verify", response_model=PaymentResponse)
async def verify_payment(
    payment_id: UUID,
    current_company: Company = Depends(get_current_company_from_jwt),
    db: AsyncSession = Depends(get_db)
):
    """
    Vérifier manuellement le statut d'un paiement auprès de FedaPay (authentification JWT)
    """
    result = await db.execute(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.company_id == current_company.id
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if not payment.fedapay_transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No FedaPay transaction ID"
        )
    
    # Vérifier auprès de FedaPay
    is_completed = fedapay_service.verify_transaction(payment.fedapay_transaction_id)
    
    if is_completed and payment.status != PaymentStatus.COMPLETED:
        # Mettre à jour le paiement
        await db.execute(
            update(Payment)
            .where(Payment.id == payment.id)
            .values(
                status=PaymentStatus.COMPLETED,
                paid_at=datetime.utcnow()
            )
        )
        
        # Activer l'abonnement (même logique que webhook)
        result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == payment.plan_id)
        )
        plan = result.scalar_one_or_none()
        
        if plan:
            if plan.billing_period == "monthly":
                expires_at = datetime.utcnow() + timedelta(days=30)
            elif plan.billing_period == "yearly":
                expires_at = datetime.utcnow() + timedelta(days=365)
            else:
                expires_at = datetime.utcnow() + timedelta(days=30)
            
            await db.execute(
                update(Company)
                .where(Company.id == payment.company_id)
                .values(
                    subscription_plan_id=plan.id,
                    subscription_plan=plan.name,
                    monthly_quota=plan.monthly_quota,
                    quota_used=0,
                    subscription_started_at=datetime.utcnow(),
                    subscription_expires_at=expires_at
                )
            )
        
        await db.commit()
        await db.refresh(payment)
    
    return payment
