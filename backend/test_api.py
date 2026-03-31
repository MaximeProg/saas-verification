import asyncio
import httpx
from app.db.session import AsyncSessionLocal
from app.models.admin import AdminUser
from app.models.company import Company
from app.core.security import get_password_hash, generate_api_keys, generate_webhook_secret


async def setup_test_data():
    """Crée des données de test"""
    print("🔧 Création des données de test...")
    
    async with AsyncSessionLocal() as db:
        # Créer un admin de test
        admin = AdminUser(
            username="admin",
            email="admin@kyc.com",
            password_hash=get_password_hash("admin123"),
            role="super_admin"
        )
        db.add(admin)
        
        # Créer une entreprise de test
        public_key, secret_key = generate_api_keys()
        webhook_secret = generate_webhook_secret()
        
        company = Company(
            company_name="Test Company",
            email="test@company.com",
            phone="+33612345678",
            country="France",
            address="123 Test Street",
            rccm="RC123456",
            tax_number="FR123456789",
            website="https://test.com",
            legal_representative="John Doe",
            status="production",
            is_validated=True,
            subscription_plan="business",
            monthly_quota=1000,
            quota_used=0,
            public_key=public_key,
            secret_key=secret_key,
            webhook_secret=webhook_secret
        )
        db.add(company)
        
        await db.commit()
        await db.refresh(admin)
        await db.refresh(company)
        
        print(f"✅ Admin créé: {admin.username}")
        print(f"✅ Entreprise créée: {company.company_name}")
        print(f"🔑 Secret Key: {company.secret_key}")
        
        return admin, company


async def test_api_endpoints():
    """Test des endpoints API"""
    print("\n🧪 Test des endpoints API...")
    
    # Créer données de test
    admin, company = await setup_test_data()
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1️⃣ Test Health Check...")
        response = await client.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test 2: Initier une vérification
        print("\n2️⃣ Test Initiation Vérification...")
        headers = {"Authorization": f"Bearer {company.secret_key}"}
        payload = {
            "full_name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+33612345678",
            "country": "France",
            "external_reference": "REF-001",
            "verification_type": "document"
        }
        
        response = await client.post(
            f"{base_url}/api/v1/verifications/initiate",
            json=payload,
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Vérification créée: {data['verification_id']}")
            print(f"   📍 URL: {data['verification_url']}")
            verification_id = data['verification_id']
        else:
            print(f"   ❌ Erreur: {response.text}")
            return
        
        # Test 3: Récupérer la vérification
        print("\n3️⃣ Test Récupération Vérification...")
        response = await client.get(
            f"{base_url}/api/v1/verifications/{verification_id}",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Vérification récupérée: {data['full_name']}")
            print(f"   📊 Statut: {data['status']}")
        
        # Test 4: Lister les vérifications
        print("\n4️⃣ Test Liste Vérifications...")
        response = await client.get(
            f"{base_url}/api/v1/verifications/",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {data['total']} vérifications")
            print(f"   📄 Page: {data['page']}/{data['page_size']}")
        
        print("\n🎉 Tous les tests sont passés!")


if __name__ == "__main__":
    print("⚠️  Assurez-vous que le serveur FastAPI est lancé sur http://localhost:8000")
    print("   Commande: uvicorn app.main:app --reload\n")
    
    try:
        asyncio.run(test_api_endpoints())
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
