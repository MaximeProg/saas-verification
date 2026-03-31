import asyncio
import httpx

async def test_payment():
    headers = {
        "Authorization": "Bearer sk_ag4zpz9x1eHRWljNWa0HVdSxXusn5tITSp4P7bNkPZs",
        "Content-Type": "application/json"
    }
    
    # Récupérer les plans
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/subscription-plans/public")
        plans = response.json()
        plan_id = plans[0]["id"]
        print(f"Plan sélectionné: {plans[0]['name']} - {plans[0]['price']} XOF")
        
        # Tenter le paiement
        body = {
            "plan_id": plan_id,
            "payment_method": "mobile_money",
            "customer_email": "kouassimaxime540@gmail.com",
            "customer_phone": "+22997000000",
            "callback_url": "http://localhost:3000/payment/callback",
            "return_url": "http://localhost:3000/payment/success"
        }
        
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/payments/initialize",
                headers=headers,
                json=body,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            print("\n✅ Paiement initialisé avec succès!")
            print(f"Payment ID: {data['payment_id']}")
            print(f"Reference: {data['payment_reference']}")
            print(f"Amount: {data['amount']} {data['currency']}")
            print(f"Payment URL: {data['payment_url']}")
            print(f"Status: {data['status']}")
        except httpx.HTTPStatusError as e:
            print(f"\n❌ Erreur HTTP {e.response.status_code}")
            print(f"Détails: {e.response.text}")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

asyncio.run(test_payment())
