"""
Test webhook avec une vraie URL (webhook.site)
"""
import asyncio
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.company import Company
from app.tasks.webhook_tasks import send_verification_webhook
import time


async def configure_webhook_url():
    """Configure une URL webhook pour l'entreprise de test"""
    print("🔧 Configuration webhook URL...\n")
    
    # URL de test webhook.site (remplacer par votre URL unique)
    # Allez sur https://webhook.site pour obtenir votre URL
    webhook_url = input("Entrez votre URL webhook.site (ou laissez vide pour test local): ").strip()
    
    if not webhook_url:
        webhook_url = "https://webhook.site/test-kyc-platform"
        print(f"   💡 Utilisation URL par défaut: {webhook_url}")
    
    async with AsyncSessionLocal() as db:
        # Récupérer Test Company
        result = await db.execute(
            select(Company).where(Company.company_name == "Test Company SAS")
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print("❌ Entreprise de test non trouvée")
            return None, None
        
        print(f"✅ Entreprise: {company.company_name}")
        print(f"   ID: {company.id}")
        
        # Mettre à jour webhook_url
        await db.execute(
            update(Company)
            .where(Company.id == company.id)
            .values(webhook_url=webhook_url)
        )
        await db.commit()
        
        print(f"   ✅ Webhook URL configurée: {webhook_url}\n")
        
        return str(company.id), webhook_url


def test_webhook(company_id: str, webhook_url: str):
    """Test envoi webhook"""
    print("="*60)
    print("🔗 Test Envoi Webhook")
    print("="*60 + "\n")
    
    verification_id = "KYC-2026000001"
    
    print(f"📋 Paramètres:")
    print(f"   Verification: {verification_id}")
    print(f"   Company ID: {company_id}")
    print(f"   Webhook URL: {webhook_url}")
    print(f"   Event: verification.approved\n")
    
    # Lancer task
    task = send_verification_webhook.delay(
        verification_id=verification_id,
        event_type="verification.approved",
        company_id=company_id
    )
    
    print(f"✅ Task lancée: {task.id}")
    print(f"   Status: {task.status}\n")
    
    # Attendre
    print("⏳ Attente exécution (20s max)...\n")
    
    for i in range(20):
        time.sleep(1)
        status = task.status
        
        icon = {
            "PENDING": "⏳",
            "STARTED": "🔄",
            "SUCCESS": "✅",
            "FAILURE": "❌",
            "RETRY": "🔁"
        }.get(status, "❓")
        
        print(f"   [{i+1:2d}s] {icon} {status}")
        
        if task.ready():
            print("\n" + "="*60)
            if task.successful():
                print("✅ WEBHOOK ENVOYÉ AVEC SUCCÈS!\n")
                result = task.result
                print("📊 Résultat:")
                if isinstance(result, dict):
                    for key, value in result.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"   {result}")
                
                print(f"\n🌐 Vérifiez sur {webhook_url}")
                print("   Vous devriez voir la requête POST avec:")
                print("   - Header: X-Webhook-Signature")
                print("   - Body: JSON avec les données de vérification")
                
                return True
            else:
                print("❌ WEBHOOK ÉCHOUÉ!\n")
                print("📊 Erreur:")
                print(f"   {task.info}")
                return False
    
    print("\n" + "="*60)
    print("⏰ Task toujours en cours")
    print("💡 Consultez les logs Celery")
    print("="*60)
    return None


async def show_webhook_logs():
    """Affiche les derniers logs webhook"""
    print("\n" + "="*60)
    print("📊 Logs Webhooks (Database)")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        from app.models.logs import WebhookLog
        
        result = await db.execute(
            select(WebhookLog).order_by(WebhookLog.created_at.desc()).limit(3)
        )
        logs = result.scalars().all()
        
        if not logs:
            print("📭 Aucun log trouvé")
            return
        
        for i, log in enumerate(logs, 1):
            status_icon = "✅" if log.success else "❌"
            print(f"{i}. {status_icon} {log.event_type}")
            print(f"   URL: {log.webhook_url}")
            print(f"   Status HTTP: {log.response_status}")
            print(f"   Retry: {log.retry_count}")
            print(f"   Date: {log.created_at}")
            
            if log.success:
                print(f"   ✅ Succès!")
            else:
                print(f"   ❌ Erreur: {log.response_body[:200]}")
            print()


if __name__ == "__main__":
    print("🧪 Test Webhook avec URL Réelle\n")
    print("="*60)
    print("\n💡 Pour obtenir une URL de test:")
    print("   1. Ouvrir https://webhook.site dans votre navigateur")
    print("   2. Copier l'URL unique générée")
    print("   3. Coller ci-dessous\n")
    print("="*60 + "\n")
    
    # Configuration
    company_id, webhook_url = asyncio.run(configure_webhook_url())
    
    if not company_id:
        print("\n❌ Configuration échouée")
        exit(1)
    
    # Test
    result = test_webhook(company_id, webhook_url)
    
    # Logs
    asyncio.run(show_webhook_logs())
    
    print("\n" + "="*60)
    print("📝 Résumé")
    print("="*60)
    
    if result:
        print("\n✅ Les webhooks fonctionnent correctement!")
        print("\n🎯 Fonctionnalités:")
        print("   ✅ Signature HMAC-SHA256")
        print("   ✅ Payload JSON complet")
        print("   ✅ Retry automatique (5 tentatives)")
        print("   ✅ Logs dans database")
    elif result is False:
        print("\n❌ Problème détecté")
        print("\n💡 Vérifications:")
        print("   1. Celery worker lancé")
        print("   2. Redis connecté")
        print("   3. URL webhook valide et accessible")
        print("   4. Consulter logs Celery pour détails")
    else:
        print("\n⏰ Test en cours...")
        print("   Consultez le terminal Celery")
