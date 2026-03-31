import asyncio
from sqlalchemy import text
from app.db.session import engine, AsyncSessionLocal
from app.config import settings


async def test_connection():
    """Test de connexion à Neon PostgreSQL"""
    print("🔍 Test de connexion à Neon PostgreSQL...")
    print(f"📍 Base de données: {settings.DATABASE_URL.split('@')[1].split('/')[0]}")
    
    try:
        # Test connexion avec une requête simple
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connexion réussie!")
            print(f"📊 Version PostgreSQL: {version[:50]}...")
            
            # Test création d'une table simple
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100)
                )
            """))
            print("✅ Test création table: OK")
            
            # Nettoyer
            await conn.execute(text("DROP TABLE IF EXISTS test_table"))
            print("✅ Test suppression table: OK")
        
        # Test session async
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✅ Test session async: {test_value}")
        
        print("\n🎉 Tous les tests de connexion sont passés!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())
