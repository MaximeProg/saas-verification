import asyncio
from app.db.session import engine
from app.models import Base


async def init_database():
    """Initialise toutes les tables dans Neon PostgreSQL"""
    print("🔧 Initialisation de la base de données...")
    
    try:
        async with engine.begin() as conn:
            # Créer toutes les tables
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Toutes les tables ont été créées avec succès!")
        print("\n📊 Tables créées:")
        print("  - companies (Entreprises)")
        print("  - verifications (Vérifications KYC)")
        print("  - admin_users (Administrateurs)")
        print("  - api_logs (Logs API)")
        print("  - webhook_logs (Logs Webhooks)")
        print("  - email_logs (Logs Emails)")
        print("  - blacklist (Liste noire)")
        print("  - verification_duplicates (Détection doublons)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
