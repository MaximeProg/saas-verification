"""Test pour vérifier l'envoi des informations client à FedaPay"""
from app.services.fedapay import fedapay_service
import json

print("Test d'envoi des informations client à FedaPay\n")

result = fedapay_service.create_transaction(
    amount=15000,
    currency="XOF",
    description="Test avec informations client",
    customer_email="kouassimaxime540@gmail.com",
    customer_phone="+22997000000",
    callback_url="http://localhost:3000/callback",
    metadata={"test": "customer_info"}
)

print("Résultat:")
print(f"Success: {result.get('success')}")
print(f"Transaction ID: {result.get('transaction_id')}")

print("\nRéponse complète FedaPay:")
print(json.dumps(result.get('data'), indent=2))

# Vérifier si les infos client sont présentes
transaction = result.get('data', {}).get('v1/transaction', {})
print("\nInformations client dans la transaction:")
print(f"Customer ID: {transaction.get('customer_id')}")
print(f"Customer Email: {transaction.get('customer', {}).get('email', 'Non trouvé')}")
print(f"Customer Phone: {transaction.get('customer', {}).get('phone_number', 'Non trouvé')}")
