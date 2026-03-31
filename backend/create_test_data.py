import asyncio
from app.db.session import AsyncSessionLocal
from app.models.admin import AdminUser
from app.models.company import Company
from app.core.security import get_password_hash, generate_api_keys, generate_webhook_secret


async def create_test_data():
    """Crée des données de test pour l'API"""
    print("🔧 Création des données de test...\n")
    
    async with AsyncSessionLocal() as db:
        # 1. Créer un admin de test
        print("1️⃣ Création d'un administrateur...")
        admin = AdminUser(
            username="admin",
            email="admin@kyc.com",
            password_hash=get_password_hash("admin123"),
            role="super_admin"
        )
        db.add(admin)
        await db.flush()
        print(f"   ✅ Admin créé")
        print(f"   👤 Username: admin")
        print(f"   🔑 Password: admin123")
        
        # 2. Créer une entreprise de test
        print("\n2️⃣ Création d'une entreprise de test...")
        public_key, secret_key = generate_api_keys()
        webhook_secret = generate_webhook_secret()
        
        company = Company(
            company_name="Test Company SAS",
            email="test@company.com",
            phone="+33612345678",
            country="France",
            address="123 Avenue des Tests, 75001 Paris",
            rccm="RC-PARIS-2024-123456",
            tax_number="FR12345678901",
            website="https://testcompany.com",
            legal_representative="Jean Dupont",
            status="production",
            is_validated=True,
            subscription_plan="business",
            monthly_quota=1000,
            quota_used=0,
            public_key=public_key,
            secret_key=secret_key,
            webhook_secret=webhook_secret,
            webhook_url="https://testcompany.com/webhook"
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
        
        print(f"   ✅ Entreprise créée")
        print(f"   🏢 Nom: {company.company_name}")
        print(f"   📧 Email: {company.email}")
        print(f"   📊 Statut: {company.status}")
        print(f"   💳 Plan: {company.subscription_plan}")
        print(f"   📈 Quota: {company.quota_used}/{company.monthly_quota}")
        
        print(f"\n🔑 Clés API:")
        print(f"   Public Key:  {company.public_key}")
        print(f"   Secret Key:  {company.secret_key}")
        print(f"   Webhook Secret: {company.webhook_secret}")
        
        print(f"\n💡 Utilisez la Secret Key pour tester l'API:")
        print(f'   Authorization: Bearer {company.secret_key}')
        
        print("\n🎉 Données de test créées avec succès!")
        
        return admin, company


if __name__ == "__main__":
    asyncio.run(create_test_data())
