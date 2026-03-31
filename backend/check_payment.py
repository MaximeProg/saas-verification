import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check_payment():
    async with AsyncSessionLocal() as db:
        # Récupérer le dernier paiement
        result = await db.execute(text("""
            SELECT 
                payment_reference,
                amount,
                currency,
                status,
                fedapay_transaction_id,
                fedapay_token,
                created_at
            FROM payments 
            ORDER BY created_at DESC 
            LIMIT 1;
        """))
        
        payment = result.fetchone()
        
        if payment:
            print("✅ Dernier paiement créé:")
            print(f"  Référence: {payment[0]}")
            print(f"  Montant: {payment[1]} {payment[2]}")
            print(f"  Statut: {payment[3]}")
            print(f"  Transaction FedaPay: {payment[4]}")
            print(f"  Token: {payment[5][:50]}..." if payment[5] else "  Token: None")
            print(f"  Date: {payment[6]}")
        else:
            print("❌ Aucun paiement trouvé")

asyncio.run(check_payment())
