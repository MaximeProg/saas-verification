from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.subscription_plan import SubscriptionPlan
from app.models.admin import AdminUser
from app.schemas.subscription_plan import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    SubscriptionPlanPublic
)
from app.core.security import get_current_admin

router = APIRouter()


@router.get("/public", response_model=List[SubscriptionPlanPublic])
async def get_public_plans(
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer tous les plans actifs (endpoint public)
    """
    result = await db.execute(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.display_order)
    )
    plans = result.scalars().all()
    
    # Transformer en schéma public avec fonctionnalités
    public_plans = []
    for plan in plans:
        plan_dict = {
            "id": plan.id,
            "name": plan.name,
            "slug": plan.slug,
            "description": plan.description,
            "price": plan.price,
            "currency": plan.currency,
            "billing_period": plan.billing_period,
            "monthly_quota": plan.monthly_quota,
            "max_api_keys": plan.max_api_keys,
            "max_users": plan.max_users,
            "advantages": plan.advantages,
            "is_popular": plan.is_popular,
            "is_active": plan.is_active,
            "display_order": plan.display_order,
            "features": plan.advantages if plan.advantages else [],
            # Extraire les fonctionnalités
            "has_webhook_support": plan.features.get("webhook_support", False) if plan.features else False,
            "has_priority_support": plan.features.get("priority_support", False) if plan.features else False,
            "has_custom_branding": plan.features.get("custom_branding", False) if plan.features else False,
            "has_api_access": plan.features.get("api_access", True) if plan.features else True,
            "has_bulk_upload": plan.features.get("bulk_upload", False) if plan.features else False,
            "has_advanced_analytics": plan.features.get("advanced_analytics", False) if plan.features else False,
        }
        public_plans.append(SubscriptionPlanPublic(**plan_dict))
    
    return public_plans


@router.get("", response_model=List[SubscriptionPlanResponse])
async def get_all_plans(
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer tous les plans (admin uniquement)
    """
    result = await db.execute(
        select(SubscriptionPlan).order_by(SubscriptionPlan.display_order)
    )
    plans = result.scalars().all()
    return plans


@router.get("/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_plan(
    plan_id: UUID,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupérer un plan spécifique (admin uniquement)
    """
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    return plan


@router.post("", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: SubscriptionPlanCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Créer un nouveau plan d'abonnement (admin uniquement)
    """
    # Vérifier si le slug existe déjà
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.slug == plan_data.slug)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A plan with this slug already exists"
        )
    
    # Créer le plan
    new_plan = SubscriptionPlan(
        **plan_data.model_dump(),
        created_by=current_admin.id
    )
    
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    
    return new_plan


@router.put("/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_plan(
    plan_id: UUID,
    plan_data: SubscriptionPlanUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Mettre à jour un plan d'abonnement (admin uniquement)
    """
    # Récupérer le plan
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Mettre à jour uniquement les champs fournis
    update_data = plan_data.model_dump(exclude_unset=True)
    
    if update_data:
        await db.execute(
            update(SubscriptionPlan)
            .where(SubscriptionPlan.id == plan_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(plan)
    
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: UUID,
    current_admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprimer un plan d'abonnement (admin uniquement)
    """
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    await db.execute(
        delete(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    await db.commit()
    
    return None
