import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, update
from app.models.company import Company
from datetime import datetime

async def validate_company():
    async with AsyncSessionLocal() as db:
        # Trouver l'entreprise par email
        result = await db.execute(
            select(Company).where(Company.email == "kouassimaxime540@gmail.com")
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print("❌ Entreprise non trouvée avec l'email kouassimaxime540@gmail.com")
            return
        
        print(f"✓ Entreprise trouvée: {company.company_name}")
        print(f"  ID: {company.id}")
        print(f"  Email: {company.email}")
        print(f"  Status: {company.status}")
        print(f"  Documents soumis: {company.documents_submitted}")
        print(f"  Documents validés: {company.documents_validated}")
        
        # Valider les documents
        await db.execute(
            update(Company)
            .where(Company.id == company.id)
            .values(
                documents_validated=True,
                documents_validated_at=datetime.utcnow(),
                documents_rejection_reason=None
            )
        )
        await db.commit()
        
        print("\n✅ Documents de l'entreprise validés avec succès!")
        print(f"  Date de validation: {datetime.utcnow()}")

asyncio.run(validate_company())
