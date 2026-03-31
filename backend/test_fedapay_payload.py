"""Afficher le payload exact qui sera envoyé à FedaPay"""
import json

# Simuler la construction du payload
customer_email = "kouassimaxime540@gmail.com"
customer_phone = "+22997000000"

payload = {
    "amount": 15000,
    "currency": {
        "iso": "XOF"
    },
    "description": "Test Abonnement Starter",
}

# Ajouter les informations client
if customer_email or customer_phone:
    payload["customer"] = {}
    if customer_email:
        payload["customer"]["email"] = customer_email
    if customer_phone:
        payload["customer"]["phone_number"] = {
            "number": customer_phone,
            "country": "bj"
        }

payload["callback_url"] = "http://localhost:3000/callback"
payload["metadata"] = {"test": "true"}

print("Payload envoyé à FedaPay:")
print(json.dumps(payload, indent=2))
