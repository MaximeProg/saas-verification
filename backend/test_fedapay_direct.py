"""Test direct du service FedaPay pour identifier le problème"""
from app.services.fedapay import FedaPayService

# Créer une instance du service
service = FedaPayService()

print(f"Mode simulation: {service.simulation_mode}")
print(f"API Key configurée: {service.api_key is not None}")
print(f"Environment: {service.environment}")
print(f"Base URL: {service.base_url}")

# Tester la création d'une transaction
print("\nTest de création de transaction...")
try:
    result = service.create_transaction(
        amount=15000,
        currency="XOF",
        description="Test Abonnement Starter",
        customer_email="test@example.com",
        customer_phone="+22997000000",
        callback_url="http://localhost:3000/callback",
        metadata={"test": "true"}
    )
    
    print(f"\nRésultat:")
    print(f"Success: {result.get('success')}")
    print(f"Transaction ID: {result.get('transaction_id')}")
    print(f"Token: {result.get('token')}")
    print(f"Payment URL: {result.get('payment_url')}")
    print(f"Status: {result.get('status')}")
    
    print(f"\nRéponse complète FedaPay:")
    import json
    print(json.dumps(result.get('data'), indent=2))
    
    if not result.get('success'):
        print(f"Error: {result.get('error')}")
        
except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()
