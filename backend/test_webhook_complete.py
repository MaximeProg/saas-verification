"""
Test complet du système de webhooks
"""
import asyncio
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.company import Company
from app.models.verification import Verification
from app.tasks.webhook_tasks import send_verification_webhook
import time


async def setup_test_webhook():
    """Configure une URL webhook de test pour l'entreprise"""
    print("🔧 Configuration webhook de test...\n")
    
    async with AsyncSessionLocal() as db:
        # Récupérer Test Company
        result = await db.execute(
            select(Company).where(Company.company_name == "Test Company SAS")
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print("❌ Entreprise de test non trouvée")
            return None
        
        print(f"✅ Entreprise trouvée: {company.company_name}")
        print(f"   ID: {company.id}")
        print(f"   Webhook actuel: {company.webhook_url or 'Non configuré'}")
        
        # Configurer webhook de test (webhook.site pour tester)
        test_webhook_url = "https://webhook.site/unique-id-test"
        
        await db.execute(
            update(Company)
            .where(Company.id == company.id)
            .values(webhook_url=test_webhook_url)
        )
        await db.commit()
        
        print(f"\n✅ Webhook configuré: {test_webhook_url}")
        print("   💡 Vous pouvez créer votre propre URL sur https://webhook.site")
        
        return str(company.id)


async def get_test_verification():
    """Récupère une vérification de test"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Verification).limit(1)
        )
        verification = result.scalar_one_or_none()
        
        if verification:
            print(f"✅ Vérification trouvée: {verification.verification_id}")
            return verification.verification_id
        
        return None


def test_webhook_task(verification_id: str, company_id: str):
    """Test l'envoi d'un webhook"""
    print("\n" + "="*60)
    print("🔗 Test Envoi Webhook")
    print("="*60 + "\n")
    
    # Lancer la task
    task = send_verification_webhook.delay(
        verification_id=verification_id,
        event_type="verification.approved",
        company_id=company_id
    )
    
    print(f"✅ Task webhook lancée")
    print(f"   Task ID: {task.id}")
    print(f"   Status initial: {task.status}")
    
    # Attendre exécution
    print("\n⏳ Attente exécution (max 15s)...")
    
    for i in range(15):
        time.sleep(1)
        status = task.status
        print(f"   [{i+1}s] Status: {status}")
        
        if task.ready():
            if task.successful():
                print(f"\n✅ Webhook envoyé avec succès!")
                print(f"   Résultat: {task.result}")
                return True
            else:
                print(f"\n❌ Webhook échoué")
                print(f"   Erreur: {task.info}")
                return False
    
    print("\n⏰ Task toujours en cours après 15s")
    print("   💡 Consultez les logs Celery pour plus de détails")
    return None


async def check_webhook_logs():
    """Vérifie les logs de webhooks dans la DB"""
    print("\n" + "="*60)
    print("📊 Logs Webhooks dans Database")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        from app.models.logs import WebhookLog
        
        result = await db.execute(
            select(WebhookLog).order_by(WebhookLog.created_at.desc()).limit(5)
        )
        logs = result.scalars().all()
        
        if not logs:
            print("📭 Aucun log webhook trouvé")
            return
        
        print(f"📋 {len(logs)} derniers webhooks:\n")
        
        for log in logs:
            status_icon = "✅" if log.success else "❌"
            print(f"{status_icon} {log.event_type}")
            print(f"   URL: {log.webhook_url}")
            print(f"   Status: {log.response_status}")
            print(f"   Retry: {log.retry_count}")
            print(f"   Date: {log.created_at}")
            if not log.success:
                print(f"   Erreur: {log.response_body[:100]}")
            print()


if __name__ == "__main__":
    print("🧪 Test Complet Webhooks\n")
    print("="*60)
    
    # Setup
    company_id = asyncio.run(setup_test_webhook())
    
    if not company_id:
        print("\n❌ Impossible de configurer le test")
        exit(1)
    
    verification_id = asyncio.run(get_test_verification())
    
    if not verification_id:
        print("\n❌ Aucune vérification trouvée")
        print("💡 Créez une vérification d'abord avec: python test_api_simple.py")
        exit(1)
    
    # Test webhook
    result = test_webhook_task(verification_id, company_id)
    
    # Vérifier logs
    asyncio.run(check_webhook_logs())
    
    print("\n" + "="*60)
    if result:
        print("🎉 Test webhook réussi!")
    elif result is False:
        print("❌ Test webhook échoué")
        print("\n💡 Vérifications:")
        print("   1. Celery worker est lancé")
        print("   2. Redis est connecté")
        print("   3. URL webhook est valide")
        print("   4. Consulter logs Celery pour détails")
    else:
        print("⏰ Test en cours...")
        print("💡 Consultez le terminal Celery pour voir l'exécution")
    
    print("\n📝 Pour tester avec une vraie URL:")
    print("   1. Aller sur https://webhook.site")
    print("   2. Copier votre URL unique")
    print("   3. Mettre à jour webhook_url de l'entreprise")
    print("   4. Relancer ce test")
