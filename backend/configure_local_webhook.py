"""
Configure l'entreprise pour utiliser le serveur webhook local
"""
import asyncio
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.company import Company


async def configure():
    webhook_url = "http://localhost:5001/webhook"
    
    print("Configuration webhook local...\n")
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Company).where(Company.company_name == "Test Company SAS")
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print("Erreur: Entreprise non trouvee")
            return False
        
        print(f"Entreprise: {company.company_name}")
        print(f"ID: {company.id}")
        
        await db.execute(
            update(Company)
            .where(Company.id == company.id)
            .values(webhook_url=webhook_url)
        )
        await db.commit()
        
        print(f"\nWebhook URL configuree: {webhook_url}")
        print("\nProchaines etapes:")
        print("  1. Lancer: python webhook_server_test.py")
        print("  2. Lancer: python test_webhook_simple.py")
        print("  3. Verifier: http://localhost:5001")
        
        return True


if __name__ == "__main__":
    asyncio.run(configure())
