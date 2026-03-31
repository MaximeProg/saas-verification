"""
Recupere le webhook_secret de l'entreprise de test
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.company import Company


async def get_secret():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Company).where(Company.company_name == "Test Company SAS")
        )
        company = result.scalar_one_or_none()
        
        if company:
            print(f"Entreprise: {company.company_name}")
            print(f"Webhook Secret: {company.webhook_secret}")
            return company.webhook_secret
        else:
            print("Entreprise non trouvee")
            return None


if __name__ == "__main__":
    asyncio.run(get_secret())
