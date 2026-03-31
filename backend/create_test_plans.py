"""
Script pour créer des plans d'abonnement de test
"""
import asyncio
from sqlalchemy import insert
from app.db.session import AsyncSessionLocal
from app.models.subscription_plan import SubscriptionPlan
import uuid


async def create_test_plans():
    """Créer 3 plans d'abonnement de test"""
    
    plans = [
        {
            "id": uuid.uuid4(),
            "name": "Starter",
            "slug": "starter",
            "description": "Plan de démarrage pour petites entreprises",
            "price": 15000,
            "currency": "XOF",
            "billing_period": "monthly",
            "monthly_quota": 100,
            "max_api_keys": 3,
            "max_users": 1,
            "features": {
                "webhook_support": True,
                "priority_support": False,
                "custom_branding": False,
                "api_access": True,
                "bulk_upload": False,
                "advanced_analytics": False
            },
            "advantages": [
                "100 vérifications par mois",
                "Support email standard",
                "3 clés API",
                "Webhooks inclus",
                "Documentation complète"
            ],
            "is_active": True,
            "is_popular": False,
            "is_custom": False,
            "display_order": 1
        },
        {
            "id": uuid.uuid4(),
            "name": "Professional",
            "slug": "professional",
            "description": "Pour les entreprises en croissance",
            "price": 50000,
            "currency": "XOF",
            "billing_period": "monthly",
            "monthly_quota": 500,
            "max_api_keys": 10,
            "max_users": 5,
            "features": {
                "webhook_support": True,
                "priority_support": True,
                "custom_branding": False,
                "api_access": True,
                "bulk_upload": True,
                "advanced_analytics": True
            },
            "advantages": [
                "500 vérifications par mois",
                "Support prioritaire",
                "10 clés API",
                "5 utilisateurs",
                "Webhooks inclus",
                "Upload en masse",
                "Analytics avancées"
            ],
            "is_active": True,
            "is_popular": True,
            "is_custom": False,
            "display_order": 2
        },
        {
            "id": uuid.uuid4(),
            "name": "Enterprise",
            "slug": "enterprise",
            "description": "Solution complète pour grandes entreprises",
            "price": 150000,
            "currency": "XOF",
            "billing_period": "monthly",
            "monthly_quota": 2000,
            "max_api_keys": 50,
            "max_users": 20,
            "features": {
                "webhook_support": True,
                "priority_support": True,
                "custom_branding": True,
                "api_access": True,
                "bulk_upload": True,
                "advanced_analytics": True,
                "dedicated_support": True,
                "sla_guarantee": True
            },
            "advantages": [
                "2000 vérifications par mois",
                "Support dédié 24/7",
                "50 clés API",
                "20 utilisateurs",
                "Webhooks inclus",
                "Upload en masse",
                "Analytics avancées",
                "Branding personnalisé",
                "SLA garanti 99.9%"
            ],
            "is_active": True,
            "is_popular": False,
            "is_custom": False,
            "display_order": 3
        }
    ]
    
    async with AsyncSessionLocal() as db:
        for plan_data in plans:
            # Vérifier si le plan existe déjà
            from sqlalchemy import select
            result = await db.execute(
                select(SubscriptionPlan).where(SubscriptionPlan.slug == plan_data["slug"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⏭️  Plan '{plan_data['name']}' existe déjà")
                continue
            
            # Créer le plan
            await db.execute(
                insert(SubscriptionPlan).values(**plan_data)
            )
            print(f"✅ Plan '{plan_data['name']}' créé - {plan_data['price']} {plan_data['currency']}/mois")
        
        await db.commit()
    
    print("\n" + "="*60)
    print("✅ Plans de test créés avec succès!")
    print("="*60)
    print("\nPour voir les plans:")
    print("  GET /api/v1/subscription-plans/public")
    print("\nPour gérer les plans (admin):")
    print("  GET /api/v1/subscription-plans")


if __name__ == "__main__":
    print("🎯 Création des plans d'abonnement de test\n")
    print("="*60)
    asyncio.run(create_test_plans())
