"""
Configuration automatique webhook pour test
"""
import asyncio
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.company import Company


async def setup_webhook():
    """Configure une URL webhook de test"""
    
    # URL webhook.site publique pour tests
    # Vous pouvez créer votre propre URL sur https://webhook.site
    webhook_url = "https://webhook.site/unique-kyc-test"
    
    print("🔧 Configuration webhook URL...\n")
    
    async with AsyncSessionLocal() as db:
        # Récupérer Test Company
        result = await db.execute(
            select(Company).where(Company.company_name == "Test Company SAS")
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print("❌ Entreprise de test non trouvée")
            return False
        
        print(f"✅ Entreprise: {company.company_name}")
        print(f"   ID: {company.id}")
        print(f"   Webhook actuel: {company.webhook_url or 'Non configuré'}")
        
        # Mettre à jour
        await db.execute(
            update(Company)
            .where(Company.id == company.id)
            .values(webhook_url=webhook_url)
        )
        await db.commit()
        
        print(f"\n✅ Webhook URL configurée: {webhook_url}")
        print("\n💡 Pour voir les webhooks en temps réel:")
        print(f"   Ouvrir: {webhook_url}")
        
        return True


if __name__ == "__main__":
    print("🧪 Setup Webhook Test\n")
    print("="*60)
    
    success = asyncio.run(setup_webhook())
    
    if success:
        print("\n" + "="*60)
        print("✅ Configuration terminée!")
        print("\n🚀 Prochaine étape:")
        print("   python test_webhook_simple.py")
    else:
        print("\n❌ Configuration échouée")
