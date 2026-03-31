"""
Script pour créer les plans d'abonnement par défaut
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, get_db
from app.models.subscription_plan import SubscriptionPlan
from sqlalchemy import select


async def create_default_plans():
    """Créer les plans d'abonnement par défaut"""
    
    async with AsyncSession(engine) as db:
        # Vérifier si des plans existent déjà
        result = await db.execute(select(SubscriptionPlan))
        existing_plans = result.scalars().all()
        
        if existing_plans:
            print(f"✓ {len(existing_plans)} plan(s) d'abonnement déjà existant(s)")
            for plan in existing_plans:
                print(f"  - {plan.name}: {plan.price} {plan.currency}/mois")
            
            response = input("\nVoulez-vous recréer les plans ? (y/N): ")
            if response.lower() != 'y':
                print("Annulé.")
                return
            
            # Supprimer les plans existants
            for plan in existing_plans:
                await db.delete(plan)
            await db.commit()
            print("Plans existants supprimés.")
        
        # Créer les plans
        plans = [
            SubscriptionPlan(
                name="Starter",
                slug="starter",
                description="Plan de démarrage pour les petites entreprises",
                price=15000,  # 15 000 FCFA
                currency="XOF",
                billing_period="monthly",
                monthly_quota=100,
                max_api_keys=2,
                max_users=1,
                features={
                    "webhook_support": True,
                    "priority_support": False,
                    "custom_branding": False,
                    "api_access": True,
                    "bulk_upload": False,
                    "advanced_analytics": False
                },
                advantages=[
                    "100 vérifications par mois",
                    "Support email",
                    "Webhooks inclus",
                    "API REST complète",
                    "2 clés API"
                ],
                is_active=True,
                is_popular=False,
                display_order=1
            ),
            SubscriptionPlan(
                name="Professional",
                slug="professional",
                description="Plan professionnel pour les entreprises en croissance",
                price=50000,  # 50 000 FCFA
                currency="XOF",
                billing_period="monthly",
                monthly_quota=500,
                max_api_keys=5,
                max_users=3,
                features={
                    "webhook_support": True,
                    "priority_support": True,
                    "custom_branding": False,
                    "api_access": True,
                    "bulk_upload": True,
                    "advanced_analytics": True
                },
                advantages=[
                    "500 vérifications par mois",
                    "Support prioritaire",
                    "Webhooks avancés",
                    "API REST complète",
                    "Upload en masse",
                    "Analytiques avancées",
                    "5 clés API",
                    "3 utilisateurs"
                ],
                is_active=True,
                is_popular=True,
                display_order=2
            ),
            SubscriptionPlan(
                name="Enterprise",
                slug="enterprise",
                description="Plan entreprise pour les grandes organisations",
                price=150000,  # 150 000 FCFA
                currency="XOF",
                billing_period="monthly",
                monthly_quota=2000,
                max_api_keys=10,
                max_users=10,
                features={
                    "webhook_support": True,
                    "priority_support": True,
                    "custom_branding": True,
                    "api_access": True,
                    "bulk_upload": True,
                    "advanced_analytics": True
                },
                advantages=[
                    "2 000 vérifications par mois",
                    "Support dédié 24/7",
                    "Webhooks personnalisés",
                    "API REST complète",
                    "Upload en masse",
                    "Analytiques avancées",
                    "Branding personnalisé",
                    "10 clés API",
                    "10 utilisateurs",
                    "SLA garanti"
                ],
                is_active=True,
                is_popular=False,
                display_order=3
            )
        ]
        
        # Afficher les infos avant le commit
        print(f"\n✓ Création de {len(plans)} plans d'abonnement:")
        for plan in plans:
            print(f"  - {plan.name}: {plan.price:,} {plan.currency}/mois ({plan.monthly_quota} vérifications)")
            db.add(plan)
        
        await db.commit()
        print("\n✓ Plans créés avec succès dans la base de données!")


if __name__ == "__main__":
    print("Création des plans d'abonnement par défaut...\n")
    asyncio.run(create_default_plans())
    print("\n✓ Terminé!")
