import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check_table():
    async with AsyncSessionLocal() as db:
        # Vérifier les colonnes de la table payments
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'payments'
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        
        print("Colonnes de la table 'payments':")
        print("-" * 50)
        for col in columns:
            print(f"{col[0]:<30} {col[1]}")
        
        print("\n" + "=" * 50)
        
        # Vérifier si payment_metadata existe
        has_metadata = any(col[0] == 'payment_metadata' for col in columns)
        
        if has_metadata:
            print("✅ La colonne 'payment_metadata' existe")
        else:
            print("❌ La colonne 'payment_metadata' n'existe PAS")
            print("\nIl faut appliquer la migration manuellement:")
            print("ALTER TABLE payments ADD COLUMN payment_metadata TEXT;")

asyncio.run(check_table())
