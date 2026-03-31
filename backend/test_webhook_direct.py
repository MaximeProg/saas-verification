"""
Test webhook direct sans Celery - pour debug
"""
import requests
import hmac
import hashlib
import json
from datetime import datetime


# Configuration
webhook_url = "https://webhook.site/unique-kyc-test"
webhook_secret = "test_secret_key_123"

# Payload de test
payload = {
    "event": "verification.approved",
    "verification_id": "KYC-2026000001",
    "external_reference": "REF-001",
    "status": "approved",
    "full_name": "Jean Dupont",
    "email": "jean@example.com",
    "phone": "+33612345678",
    "country": "France",
    "document_type": "passport",
    "document_number": "12AB34567",
    "created_at": "2026-03-14T16:00:00",
    "completed_at": "2026-03-14T17:00:00",
    "rejection_reason": None,
    "timestamp": datetime.utcnow().isoformat()
}

# Générer signature HMAC
payload_str = json.dumps(payload, sort_keys=True)
signature = hmac.new(
    webhook_secret.encode(),
    payload_str.encode(),
    hashlib.sha256
).hexdigest()

print("Test Webhook Direct\n")
print("="*60)
print(f"\nURL: {webhook_url}")
print(f"Signature: {signature[:20]}...")
print("\nEnvoi webhook...")

# Envoyer
try:
    response = requests.post(
        webhook_url,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "User-Agent": "KYC-Platform-Webhook/1.0"
        },
        timeout=30
    )
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if 200 <= response.status_code < 300:
        print("\nWebhook envoye avec succes!")
        print(f"\nVerifiez sur: {webhook_url}")
    else:
        print(f"\nErreur HTTP {response.status_code}")
        
except Exception as e:
    print(f"\nErreur: {e}")

print("\n" + "="*60)
