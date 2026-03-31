import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.company import Company

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Company).order_by(Company.created_at.desc()).limit(1)
        )
        company = result.scalar_one_or_none()
        
        if company:
            print(f'Company: {company.company_name}')
            print(f'Email: {company.email}')
            print(f'Status: {company.status}')
            print(f'Plan: {company.subscription_plan}')
            print(f'Quota: {company.quota_used}/{company.monthly_quota}')
            print(f'Documents submitted: {company.documents_submitted}')
            print(f'Documents validated: {company.documents_validated}')
            print(f'Public Key: {company.public_key}')
            print(f'Secret Key: {company.secret_key}')
        else:
            print('No company found')

asyncio.run(check())
