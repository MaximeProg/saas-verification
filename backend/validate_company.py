import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.company import Company
from datetime import datetime

async def validate_company_documents():
    async with AsyncSessionLocal() as db:
        # Récupérer la dernière entreprise
        result = await db.execute(
            select(Company).order_by(Company.created_at.desc()).limit(1)
        )
        company = result.scalar_one_or_none()
        
        if not company:
            print('No company found')
            return
        
        print(f'Company: {company.company_name}')
        print(f'Email: {company.email}')
        print(f'Documents submitted: {company.documents_submitted}')
        print(f'Documents validated: {company.documents_validated}')
        
        # Marquer les documents comme soumis et validés
        company.documents_submitted = True
        company.documents_validated = True
        company.documents_validated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(company)
        
        print('\n✅ Documents validés avec succès!')
        print(f'Documents submitted: {company.documents_submitted}')
        print(f'Documents validated: {company.documents_validated}')
        print(f'Validated at: {company.documents_validated_at}')

asyncio.run(validate_company_documents())
