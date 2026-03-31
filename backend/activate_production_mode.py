import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, update
from app.models.company import Company
from datetime import datetime

async def activate_production():
    async with AsyncSessionLocal() as db:
        # Trouver l'entreprise
        result = await db.execute(
            select(Company).where(Company.email == "kouassimaxime540@gmail.com")
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print("❌ Entreprise non trouvée")
            return
        
        print(f"Entreprise: {company.company_name}")
        print(f"Statut actuel: {company.status}")
        print(f"Documents validés: {company.documents_validated}")
        print(f"Compte validé: {company.is_validated}")
        
        # Activer le mode production
        await db.execute(
            update(Company)
            .where(Company.id == company.id)
            .values(
                status="production",
                is_validated=True,
                validated_at=datetime.utcnow()
            )
        )
        await db.commit()
        
        print("\n✅ Compte activé en mode PRODUCTION!")
        print("  Status: sandbox → production")
        print("  Compte validé: True")

asyncio.run(activate_production())
