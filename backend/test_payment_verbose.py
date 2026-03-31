import asyncio
import httpx
import json

async def test_payment():
    headers = {
        "Authorization": "Bearer sk_ag4zpz9x1eHRWljNWa0HVdSxXusn5tITSp4P7bNkPZs",
        "Content-Type": "application/json"
    }
    
    # Récupérer les plans
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Récupération des plans...")
        response = await client.get("http://localhost:8000/api/v1/subscription-plans/public")
        plans = response.json()
        plan_id = plans[0]["id"]
        print(f"✓ Plan sélectionné: {plans[0]['name']} - {plans[0]['price']} XOF\n")
        
        # Tenter le paiement
        body = {
            "plan_id": plan_id,
            "payment_method": "mobile_money",
            "customer_email": "kouassimaxime540@gmail.com",
            "customer_phone": "+22997000000",
            "callback_url": "http://localhost:3000/payment/callback",
            "return_url": "http://localhost:3000/payment/success"
        }
        
        print("Initialisation du paiement...")
        print(f"Body: {json.dumps(body, indent=2)}\n")
        
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/payments/initialize",
                headers=headers,
                json=body
            )
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCCÈS - Paiement initialisé!")
                print(f"Payment ID: {data.get('payment_id')}")
                print(f"Reference: {data.get('payment_reference')}")
                print(f"Amount: {data.get('amount')} {data.get('currency')}")
                print(f"Payment URL: {data.get('payment_url')}")
                print(f"Status: {data.get('status')}")
            else:
                print(f"\n❌ Erreur HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
                # Essayer de parser le JSON pour plus de détails
                try:
                    error_data = response.json()
                    print(f"\nDétails de l'erreur:")
                    print(json.dumps(error_data, indent=2))
                except:
                    pass
                    
        except Exception as e:
            print(f"\n❌ Exception: {type(e).__name__}")
            print(f"Message: {str(e)}")

asyncio.run(test_payment())
