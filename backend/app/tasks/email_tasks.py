from celery import Task
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import asyncio
from typing import Optional
from sqlalchemy import insert

from app.celery_app import celery_app
from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.logs import EmailLog


class EmailTask(Task):
    """Task de base pour envoi d'emails"""
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Envoie un email via SMTP
        
        Args:
            to_email: Destinataire
            subject: Sujet
            html_content: Contenu HTML
            text_content: Contenu texte (fallback)
        
        Returns:
            bool: Succès ou échec
        """
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            raise ValueError("Configuration SMTP manquante")
        
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        msg['To'] = to_email
        
        # Ajouter contenu texte
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        # Ajouter contenu HTML
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Envoyer
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="app.tasks.email_tasks.send_verification_initiated_email",
    max_retries=3,
    default_retry_delay=60
)
def send_verification_initiated_email(
    self,
    recipient_email: str,
    recipient_name: str,
    verification_id: str,
    verification_url: str
):
    """
    Envoie un email de notification de vérification initiée
    """
    try:
        subject = "Vérification d'identité - Action requise"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .button {{ display: inline-block; background: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Vérification d'Identité</h1>
                </div>
                <div class="content">
                    <p>Bonjour {recipient_name},</p>
                    
                    <p>Une demande de vérification d'identité a été initiée pour vous.</p>
                    
                    <p><strong>Référence:</strong> {verification_id}</p>
                    
                    <p>Pour compléter votre vérification, veuillez cliquer sur le bouton ci-dessous et suivre les instructions:</p>
                    
                    <center>
                        <a href="{verification_url}" class="button">Compléter ma vérification</a>
                    </center>
                    
                    <p><small>Ce lien est valide pendant 24 heures.</small></p>
                    
                    <p>Si vous n'avez pas demandé cette vérification, veuillez ignorer cet email.</p>
                </div>
                <div class="footer">
                    <p>KYC Platform - Vérification d'identité sécurisée</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Bonjour {recipient_name},
        
        Une demande de vérification d'identité a été initiée pour vous.
        
        Référence: {verification_id}
        
        Pour compléter votre vérification, veuillez visiter:
        {verification_url}
        
        Ce lien est valide pendant 24 heures.
        
        Si vous n'avez pas demandé cette vérification, veuillez ignorer cet email.
        
        KYC Platform
        """
        
        # Envoyer l'email
        success = self.send_email(recipient_email, subject, html_content, text_content)
        
        # Logger dans la DB
        async def log_email():
            async with AsyncSessionLocal() as db:
                await db.execute(
                    insert(EmailLog).values(
                        recipient_email=recipient_email,
                        recipient_type="user",
                        subject=subject,
                        template_name="verification_initiated",
                        status="sent" if success else "failed",
                        sent_at=datetime.utcnow() if success else None
                    )
                )
                await db.commit()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(log_email())
        loop.close()
        
        return {"success": True, "recipient": recipient_email}
        
    except Exception as exc:
        # Logger l'erreur
        async def log_error():
            async with AsyncSessionLocal() as db:
                await db.execute(
                    insert(EmailLog).values(
                        recipient_email=recipient_email,
                        recipient_type="user",
                        subject=subject,
                        template_name="verification_initiated",
                        status="failed",
                        error_message=str(exc)
                    )
                )
                await db.commit()
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(log_error())
            finally:
                loop.close()
        except Exception:
            pass
        
        # Retry
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="app.tasks.email_tasks.send_verification_completed_email",
    max_retries=3
)
def send_verification_completed_email(
    self,
    recipient_email: str,
    recipient_name: str,
    verification_id: str,
    status: str,  # 'approved' or 'rejected'
    rejection_reason: Optional[str] = None
):
    """
    Envoie un email de notification de vérification complétée
    """
    try:
        if status == "approved":
            subject = "✅ Vérification d'identité approuvée"
            status_text = "approuvée"
            status_color = "#10B981"
        else:
            subject = "❌ Vérification d'identité rejetée"
            status_text = "rejetée"
            status_color = "#EF4444"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {status_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 30px; }}
                .status {{ background: {status_color}; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Vérification d'Identité</h1>
                </div>
                <div class="content">
                    <p>Bonjour {recipient_name},</p>
                    
                    <p>Votre vérification d'identité a été <strong>{status_text}</strong>.</p>
                    
                    <div class="status">
                        <h2>{subject}</h2>
                    </div>
                    
                    <p><strong>Référence:</strong> {verification_id}</p>
                    
                    {f'<p><strong>Raison du rejet:</strong> {rejection_reason}</p>' if rejection_reason else ''}
                    
                    <p>Pour toute question, n'hésitez pas à nous contacter.</p>
                </div>
                <div class="footer">
                    <p>KYC Platform - Vérification d'identité sécurisée</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success = self.send_email(recipient_email, subject, html_content)
        
        return {"success": True, "recipient": recipient_email, "status": status}
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
