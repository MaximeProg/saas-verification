import requests
import json

# Connexion pour obtenir le token
login_response = requests.post(
    "http://localhost:8000/api/v1/companies/login",
    json={
        "email": "kouassimaxime540@gmail.com",
        "password": "Max123@@"
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print("Token obtenu avec succès")
    print(f"Token: {token[:50]}...")
    
    # Appeler l'endpoint /companies/me
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(
        "http://localhost:8000/api/v1/companies/me",
        headers=headers
    )
    
    if me_response.status_code == 200:
        company_data = me_response.json()
        print("\n" + "=" * 70)
        print("DONNÉES RETOURNÉES PAR /companies/me:")
        print("=" * 70)
        print(json.dumps(company_data, indent=2))
        
        print("\n" + "=" * 70)
        print("CHAMPS IMPORTANTS:")
        print("=" * 70)
        print(f"Status: {company_data.get('status')}")
        print(f"is_validated: {company_data.get('is_validated')}")
        print(f"documents_submitted: {company_data.get('documents_submitted')}")
        print(f"documents_validated: {company_data.get('documents_validated')}")
        print(f"documents_validated_at: {company_data.get('documents_validated_at')}")
    else:
        print(f"\nErreur /companies/me: {me_response.status_code}")
        print(me_response.text)
else:
    print(f"Erreur login: {login_response.status_code}")
    print(login_response.text)
