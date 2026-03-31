from celery import Task
import requests
import hmac
import hashlib
import json
from datetime import datetime
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from typing import Optional

from app.celery_app import celery_app
from app.config import settings
from app.models.logs import WebhookLog
from app.models.company import Company
from app.models.verification import Verification


class WebhookTask(Task):
    """Task de base pour webhooks"""
    
    def generate_signature(self, payload: dict, secret: str) -> str:
        """
        Génère une signature HMAC pour le webhook
        
        Args:
            payload: Données du webhook
            secret: Secret de l'entreprise
        
        Returns:
            str: Signature HMAC
        """
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def send_webhook(
        self,
        webhook_url: str,
        payload: dict,
        signature: str,
        timeout: int = 30
    ) -> tuple[bool, int, str]:
        """
        Envoie un webhook HTTP POST (synchrone)
        
        Args:
            webhook_url: URL du webhook
            payload: Données à envoyer
            signature: Signature HMAC
            timeout: Timeout en secondes
        
        Returns:
            tuple: (success, status_code, response_body)
        """
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "User-Agent": "KYC-Platform-Webhook/1.0"
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        success = 200 <= response.status_code < 300
        return success, response.status_code, response.text


@celery_app.task(
    bind=True,
    base=WebhookTask,
    name="app.tasks.webhook_tasks.send_verification_webhook",
    max_retries=5,
    default_retry_delay=300  # 5 minutes
)
def send_verification_webhook(
    self,
    verification_id: str,
    event_type: str,
    company_id: str
):
    """
    Envoie un webhook pour notifier l'entreprise (version synchrone)
    """
    # Créer session synchrone
    sync_engine = create_engine(
        settings.DATABASE_URL.replace("+asyncpg", "").replace("?sslmode=require&channel_binding=require", ""),
        connect_args={"sslmode": "require"}
    )
    Session = sessionmaker(bind=sync_engine)
    
    try:
        with Session() as db:
            # Récupérer l'entreprise
            company = db.execute(
                select(Company).where(Company.id == company_id)
            ).scalar_one_or_none()
            
            if not company or not company.webhook_url:
                return {"success": False, "reason": "No webhook URL configured"}
            
            # Récupérer la vérification
            verification = db.execute(
                select(Verification).where(Verification.verification_id == verification_id)
            ).scalar_one_or_none()
            
            if not verification:
                return {"success": False, "reason": "Verification not found"}
            
            # Construire le payload
            payload = {
                "event": event_type,
                "verification_id": verification.verification_id,
                "external_reference": verification.external_reference,
                "status": verification.status,
                "full_name": verification.full_name,
                "email": verification.email,
                "phone": verification.phone,
                "country": verification.country,
                "document_type": verification.document_type,
                "document_number": verification.document_number,
                "created_at": verification.created_at.isoformat() if verification.created_at else None,
                "completed_at": verification.completed_at.isoformat() if verification.completed_at else None,
                "rejection_reason": verification.rejection_reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Générer signature
            signature = self.generate_signature(payload, company.webhook_secret)
            
            # Envoyer webhook
            try:
                success, status_code, response_body = self.send_webhook(
                    company.webhook_url,
                    payload,
                    signature
                )
                
                # Logger dans la DB
                db.execute(
                    insert(WebhookLog).values(
                        verification_id=verification.id,
                        company_id=company.id,
                        event_type=event_type,
                        webhook_url=company.webhook_url,
                        payload=payload,
                        response_status=status_code,
                        response_body=response_body[:1000],
                        retry_count=self.request.retries,
                        success=success
                    )
                )
                db.commit()
                
                if not success:
                    raise Exception(f"Webhook failed with status {status_code}")
                
                return {
                    "success": True,
                    "status_code": status_code,
                    "verification_id": verification_id
                }
                
            except Exception as exc:
                # Logger l'erreur
                db.execute(
                    insert(WebhookLog).values(
                        verification_id=verification.id,
                        company_id=company.id,
                        event_type=event_type,
                        webhook_url=company.webhook_url,
                        payload=payload,
                        response_status=0,
                        response_body=str(exc)[:1000],
                        retry_count=self.request.retries,
                        success=False
                    )
                )
                db.commit()
                
                # Retry avec backoff exponentiel
                countdown = 300 * (2 ** self.request.retries)
                raise self.retry(exc=exc, countdown=countdown)
    
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
    finally:
        sync_engine.dispose()


@celery_app.task(
    name="app.tasks.webhook_tasks.send_verification_status_change",
    max_retries=5
)
def send_verification_status_change(
    verification_id: str,
    old_status: str,
    new_status: str,
    company_id: str
):
    """
    Envoie un webhook lors d'un changement de statut
    """
    event_map = {
        "pending": "verification.pending",
        "in_review": "verification.in_review",
        "approved": "verification.approved",
        "rejected": "verification.rejected"
    }
    
    event_type = event_map.get(new_status, "verification.updated")
    
    return send_verification_webhook.delay(
        verification_id=verification_id,
        event_type=event_type,
        company_id=company_id
    )
