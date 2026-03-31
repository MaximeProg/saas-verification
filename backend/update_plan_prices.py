import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, update
from app.models.subscription_plan import SubscriptionPlan

async def update_prices():
    async with AsyncSessionLocal() as db:
        # Récupérer tous les plans
        result = await db.execute(
            select(SubscriptionPlan).order_by(SubscriptionPlan.display_order)
        )
        plans = result.scalars().all()
        
        # Nouveaux prix pour les tests
        new_prices = {
            "Starter": 250,
            "Professional": 300,
            "Enterprise": 500
        }
        
        print("Mise a jour des prix des plans...")
        print("=" * 70)
        
        for plan in plans:
            if plan.name in new_prices:
                old_price = plan.price
                new_price = new_prices[plan.name]
                
                await db.execute(
                    update(SubscriptionPlan)
                    .where(SubscriptionPlan.id == plan.id)
                    .values(price=new_price)
                )
                
                print(f"{plan.name}: {old_price} XOF -> {new_price} XOF")
        
        await db.commit()
        print("\n" + "=" * 70)
        print("Prix mis a jour avec succes!")

asyncio.run(update_prices())
