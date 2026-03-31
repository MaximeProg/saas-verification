import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.company import Company

async def check_status():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Company).where(Company.email == "kouassimaxime540@gmail.com")
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print("❌ Entreprise non trouvée")
            return
        
        print("=" * 70)
        print(f"ENTREPRISE: {company.company_name}")
        print("=" * 70)
        print(f"\nSTATUT DU COMPTE:")
        print(f"  Status: {company.status}")
        print(f"  Compte valide (is_validated): {company.is_validated}")
        print(f"  Date validation compte: {company.validated_at}")
        
        print(f"\nSTATUT DES DOCUMENTS:")
        print(f"  Documents soumis: {company.documents_submitted}")
        print(f"  Documents valides: {company.documents_validated}")
        print(f"  Date validation documents: {company.documents_validated_at}")
        print(f"  Raison rejet: {company.documents_rejection_reason or 'N/A'}")
        
        print(f"\nABONNEMENT:")
        print(f"  Plan: {company.subscription_plan}")
        print(f"  Quota mensuel: {company.monthly_quota}")
        print(f"  Quota utilise: {company.quota_used}")
        print(f"  Expire le: {company.subscription_expires_at}")
        
        print(f"\nINFORMATIONS BUSINESS:")
        print(f"  Telephone: {company.phone or 'Non renseigne'}")
        print(f"  Adresse: {company.address or 'Non renseignee'}")
        print(f"  RCCM: {company.rccm or 'Non renseigne'}")
        print(f"  IFU: {company.tax_number or 'Non renseigne'}")
        print(f"  Representant: {company.legal_representative or 'Non renseigne'}")
        
        print("\n" + "=" * 70)
        print("ANALYSE:")
        print("=" * 70)
        
        if company.status == "production" and not company.documents_validated:
            print("ALERTE - INCOHERENCE DETECTEE:")
            print("   Le compte est en PRODUCTION mais les documents ne sont PAS valides")
            print("   Cela ne devrait pas etre possible!")
        elif company.status == "sandbox" and company.documents_validated:
            print("INFO: Le compte a des documents valides mais est encore en SANDBOX")
            print("   Il faut passer en PRODUCTION")
        else:
            print("OK - Coherence respectee")

asyncio.run(check_status())
