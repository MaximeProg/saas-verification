import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.subscription_plan import SubscriptionPlan

async def check_plans():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SubscriptionPlan).order_by(SubscriptionPlan.display_order)
        )
        plans = result.scalars().all()
        
        print("Plans d'abonnement dans la base de données:")
        print("=" * 70)
        for plan in plans:
            print(f"\nPlan: {plan.name}")
            print(f"  ID: {plan.id}")
            print(f"  Prix: {plan.price} {plan.currency}")
            print(f"  Quota: {plan.monthly_quota}")
            print(f"  Actif: {plan.is_active}")
            print(f"  Populaire: {plan.is_popular}")
            print(f"  Features: {len(plan.features) if plan.features else 0}")

asyncio.run(check_plans())
