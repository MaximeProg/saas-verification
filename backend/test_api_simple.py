import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
SECRET_KEY = "sk_Dqm1Z5VEw0W-5MrtBvkWsoNPQ42Hbv6LWPsTJDCor7A"

print("🧪 Test de l'API KYC Platform\n")

# Test 1: Health Check
print("1️⃣ Test Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print("   ✅ Health check OK\n")
except Exception as e:
    print(f"   ❌ Erreur: {e}\n")

# Test 2: Initier une vérification
print("2️⃣ Test Initiation Vérification...")
headers = {
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "full_name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "phone": "+33612345678",
    "country": "France",
    "external_reference": "REF-TEST-001",
    "verification_type": "document"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/verifications/initiate",
        json=payload,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"   ✅ Vérification créée!")
        print(f"   📋 ID: {data['verification_id']}")
        print(f"   🔗 URL: {data['verification_url']}")
        print(f"   📊 Statut: {data['status']}\n")
        
        verification_id = data['verification_id']
        
        # Test 3: Récupérer la vérification
        print("3️⃣ Test Récupération Vérification...")
        response = requests.get(
            f"{BASE_URL}/api/v1/verifications/{verification_id}",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Vérification récupérée")
            print(f"   👤 Nom: {data['full_name']}")
            print(f"   📧 Email: {data['email']}")
            print(f"   📊 Statut: {data['status']}\n")
        
        # Test 4: Lister les vérifications
        print("4️⃣ Test Liste Vérifications...")
        response = requests.get(
            f"{BASE_URL}/api/v1/verifications/",
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Liste récupérée")
            print(f"   📊 Total: {data['total']} vérifications")
            print(f"   📄 Page: {data['page']}/{data['page_size']}\n")
    else:
        print(f"   ❌ Erreur: {response.text}\n")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}\n")

print("🎉 Tests terminés!")
print(f"\n📚 Documentation API: {BASE_URL}/docs")
