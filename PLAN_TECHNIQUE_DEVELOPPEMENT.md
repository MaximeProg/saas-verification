# Plan Technique de Développement - Plateforme SaaS KYC

## 📋 Vue d'ensemble du projet

**Objectif** : Plateforme SaaS de vérification d'identité (KYC) permettant aux entreprises d'intégrer un service de vérification via API avec redirection sécurisée.

**Stack Technologique Principale** :
- **Backend** : FastAPI (Python)
- **Frontend** : Next.js (React)
- **Base de données** : PostgreSQL
- **Cache & Queue** : Redis
- **Task Queue** : Celery
- **Stockage média** : Cloudinary
- **Serveur** : Gunicorn + Uvicorn workers

---

## 🏗️ Architecture Globale

### Architecture en 3 couches

```
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                       │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Dashboard Admin │  │ Dashboard Client │                │
│  │    (Next.js)     │  │    (Next.js)     │                │
│  └──────────────────┘  └──────────────────┘                │
│           │                      │                           │
│           └──────────┬───────────┘                           │
└──────────────────────┼───────────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────────┐
│                COUCHE API & LOGIQUE                          │
│  ┌────────────────────────────────────────────┐             │
│  │         FastAPI Backend (async)             │             │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │             │
│  │  │   API    │  │  Auth    │  │ Webhook  │ │             │
│  │  │ Endpoints│  │  JWT     │  │ Handler  │ │             │
│  │  └──────────┘  └──────────┘  └──────────┘ │             │
│  └────────────────────────────────────────────┘             │
│           │                      │                           │
│  ┌────────┴──────────┐  ┌───────┴────────┐                 │
│  │  Celery Workers   │  │  Redis Cache   │                 │
│  │  - Compression    │  │  - Sessions    │                 │
│  │  - Upload Cloud   │  │  - Rate Limit  │                 │
│  │  - Email SMTP     │  │  - Quotas      │                 │
│  │  - Webhooks       │  └────────────────┘                 │
│  └───────────────────┘                                      │
└──────────────────────┼───────────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────────┐
│                 COUCHE DONNÉES                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   PostgreSQL     │  │   Cloudinary     │                │
│  │   (asyncpg)      │  │  (Media Storage) │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Schéma de Base de Données PostgreSQL

### Tables Principales

#### 1. **companies** (Entreprises clientes)
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    country VARCHAR(100),
    address TEXT,
    rccm VARCHAR(100),
    tax_number VARCHAR(100),
    website VARCHAR(255),
    legal_representative VARCHAR(255),
    
    -- Statut et environnement
    status VARCHAR(50) DEFAULT 'sandbox', -- sandbox, production, suspended
    is_validated BOOLEAN DEFAULT FALSE,
    validated_at TIMESTAMP,
    validated_by UUID REFERENCES admin_users(id),
    
    -- Abonnement
    subscription_plan VARCHAR(50), -- starter, business, enterprise
    monthly_quota INTEGER,
    quota_used INTEGER DEFAULT 0,
    subscription_expires_at TIMESTAMP,
    
    -- Sécurité
    public_key VARCHAR(255) UNIQUE,
    secret_key VARCHAR(255) UNIQUE,
    webhook_url VARCHAR(500),
    webhook_secret VARCHAR(255),
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_public_key (public_key)
);
```

#### 2. **verifications** (Vérifications KYC)
```sql
CREATE TABLE verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id VARCHAR(50) UNIQUE NOT NULL, -- KYC-20260001
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Informations utilisateur
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    country VARCHAR(100),
    external_reference VARCHAR(255), -- Référence entreprise
    
    -- Type et statut
    verification_type VARCHAR(50), -- document, database, full
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_review, approved, rejected, expired
    
    -- Session
    session_token VARCHAR(255) UNIQUE,
    session_url TEXT,
    session_expires_at TIMESTAMP,
    
    -- Document
    document_type VARCHAR(50), -- passport, id_card, driver_license
    document_number VARCHAR(100),
    document_front_url TEXT,
    document_back_url TEXT,
    selfie_url TEXT,
    
    -- Validation
    reviewed_by UUID REFERENCES admin_users(id),
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Sécurité et tracking
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_info JSONB,
    country_detected VARCHAR(100),
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Index
    INDEX idx_verification_id (verification_id),
    INDEX idx_company_id (company_id),
    INDEX idx_status (status),
    INDEX idx_email (email),
    INDEX idx_document_number (document_number),
    INDEX idx_created_at (created_at)
);
```

#### 3. **admin_users** (Administrateurs)
```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    role VARCHAR(50) DEFAULT 'admin', -- super_admin, admin, reviewer
    is_active BOOLEAN DEFAULT TRUE,
    
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

#### 4. **api_logs** (Logs API)
```sql
CREATE TABLE api_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    request_body JSONB,
    response_body JSONB,
    
    execution_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_company_id (company_id),
    INDEX idx_created_at (created_at),
    INDEX idx_endpoint (endpoint)
);
```

#### 5. **webhook_logs** (Logs Webhooks)
```sql
CREATE TABLE webhook_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID REFERENCES verifications(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    
    event_type VARCHAR(100), -- verification.completed, verification.approved, etc.
    webhook_url TEXT,
    
    payload JSONB,
    response_status INTEGER,
    response_body TEXT,
    
    retry_count INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_verification_id (verification_id),
    INDEX idx_company_id (company_id),
    INDEX idx_success (success)
);
```

#### 6. **email_logs** (Logs Emails SMTP)
```sql
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_email VARCHAR(255),
    recipient_type VARCHAR(50), -- company, admin, user
    
    subject VARCHAR(500),
    template_name VARCHAR(100),
    
    status VARCHAR(50), -- sent, failed, pending
    error_message TEXT,
    
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_recipient_email (recipient_email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 7. **blacklist** (Liste noire)
```sql
CREATE TABLE blacklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    type VARCHAR(50), -- email, document_number, ip, phone
    value VARCHAR(255) NOT NULL,
    
    reason TEXT,
    added_by UUID REFERENCES admin_users(id),
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_type_value (type, value),
    INDEX idx_is_active (is_active)
);
```

#### 8. **verification_duplicates** (Détection doublons)
```sql
CREATE TABLE verification_duplicates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    document_number VARCHAR(100),
    email VARCHAR(255),
    
    verification_count INTEGER DEFAULT 1,
    last_verification_id UUID REFERENCES verifications(id),
    
    is_flagged BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_document_number (document_number),
    INDEX idx_email (email)
);
```

---

## 🔧 Architecture Backend FastAPI

### Structure du projet

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── config.py               # Configuration (env variables)
│   │
│   ├── api/                    # Endpoints API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── verifications.py    # API KYC
│   │   │   ├── companies.py        # Gestion entreprises
│   │   │   ├── webhooks.py         # Webhooks
│   │   │   └── admin.py            # Admin endpoints
│   │   └── dependencies.py     # Dépendances (auth, rate limit)
│   │
│   ├── core/                   # Logique métier
│   │   ├── __init__.py
│   │   ├── security.py         # JWT, hashing, encryption
│   │   ├── rate_limiter.py     # Rate limiting avec Redis
│   │   └── pagination.py       # Pagination utils
│   │
│   ├── models/                 # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── verification.py
│   │   ├── admin.py
│   │   └── logs.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── verification.py
│   │   ├── company.py
│   │   └── webhook.py
│   │
│   ├── services/               # Services métier
│   │   ├── __init__.py
│   │   ├── verification_service.py
│   │   ├── company_service.py
│   │   ├── webhook_service.py
│   │   └── duplicate_detection.py
│   │
│   ├── tasks/                  # Celery tasks (background)
│   │   ├── __init__.py
│   │   ├── image_tasks.py      # Compression, upload Cloudinary
│   │   ├── email_tasks.py      # Envoi emails SMTP
│   │   └── webhook_tasks.py    # Envoi webhooks
│   │
│   ├── db/                     # Database
│   │   ├── __init__.py
│   │   ├── session.py          # Async session
│   │   └── base.py             # Base models
│   │
│   └── utils/                  # Utilitaires
│       ├── __init__.py
│       ├── cloudinary_client.py
│       ├── smtp_client.py
│       └── logger.py
│
├── celery_app.py               # Configuration Celery
├── requirements.txt
└── .env
```

### Configuration principale (config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "KYC Platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Session
    SESSION_EXPIRE_HOURS: int = 24
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Point d'entrée FastAPI (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.api.v1 import verifications, companies, webhooks, admin
from app.db.session import engine
from app.models import Base

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routes
app.include_router(verifications.router, prefix=f"{settings.API_V1_PREFIX}/verifications", tags=["Verifications"])
app.include_router(companies.router, prefix=f"{settings.API_V1_PREFIX}/companies", tags=["Companies"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_PREFIX}/webhooks", tags=["Webhooks"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])

@app.on_event("startup")
async def startup():
    # Créer les tables si nécessaire
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "KYC Platform API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Database Session (db/session.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Async engine avec asyncpg
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### API Endpoint Principal - Initier Vérification

```python
# api/v1/verifications.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.verification import VerificationInitiate, VerificationResponse
from app.services.verification_service import VerificationService
from app.core.security import verify_api_key
from app.tasks.image_tasks import process_verification_images
from app.tasks.email_tasks import send_verification_initiated_email

router = APIRouter()

@router.post("/initiate", response_model=VerificationResponse)
async def initiate_verification(
    data: VerificationInitiate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    company = Depends(verify_api_key)
):
    """
    Initier une nouvelle vérification KYC
    
    Workflow:
    1. Validation quota entreprise
    2. Création vérification en DB (status: pending)
    3. Génération session token unique
    4. Réponse immédiate avec URL
    5. Background: email notification
    """
    
    # Service de vérification
    service = VerificationService(db)
    
    # Vérifier quota
    if company.quota_used >= company.monthly_quota:
        raise HTTPException(status_code=403, detail="Quota mensuel atteint")
    
    # Créer vérification (rapide, juste insertion DB)
    verification = await service.create_verification(
        company_id=company.id,
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        country=data.country,
        external_reference=data.external_reference,
        verification_type=data.verification_type
    )
    
    # Incrémenter quota
    await service.increment_quota(company.id)
    
    # Background task: email
    background_tasks.add_task(
        send_verification_initiated_email,
        email=data.email,
        verification_id=verification.verification_id
    )
    
    # Réponse immédiate
    return VerificationResponse(
        verification_id=verification.verification_id,
        verification_url=verification.session_url,
        status=verification.status
    )
```

### Celery Configuration (celery_app.py)

```python
from celery import Celery
from app.config import settings

celery_app = Celery(
    "kyc_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    worker_prefetch_multiplier=4,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
```

### Tâche Celery - Compression Images (tasks/image_tasks.py)

```python
from celery import shared_task
import cloudinary.uploader
from PIL import Image
import io
from app.utils.cloudinary_client import upload_to_cloudinary
from app.db.session import AsyncSessionLocal
from app.models.verification import Verification

@shared_task(bind=True, max_retries=3)
def compress_and_upload_image(self, image_data: bytes, verification_id: str, image_type: str):
    """
    Compresse et upload image vers Cloudinary
    
    Args:
        image_data: Données brutes de l'image
        verification_id: ID de la vérification
        image_type: front, back, selfie
    """
    try:
        # Compression avec Pillow
        img = Image.open(io.BytesIO(image_data))
        
        # Redimensionner si trop grand
        max_size = (1920, 1080)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convertir en JPEG avec compression
        output = io.BytesIO()
        img.convert("RGB").save(output, format="JPEG", quality=85, optimize=True)
        output.seek(0)
        
        # Upload vers Cloudinary avec transformations
        result = cloudinary.uploader.upload(
            output,
            folder=f"kyc/{verification_id}",
            resource_type="image",
            format="jpg",
            transformation=[
                {"quality": "auto:good"},
                {"fetch_format": "auto"}
            ]
        )
        
        # Mettre à jour DB avec URL sécurisée
        async def update_db():
            async with AsyncSessionLocal() as session:
                verification = await session.get(Verification, verification_id)
                if image_type == "front":
                    verification.document_front_url = result["secure_url"]
                elif image_type == "back":
                    verification.document_back_url = result["secure_url"]
                elif image_type == "selfie":
                    verification.selfie_url = result["secure_url"]
                await session.commit()
        
        # Exécuter update
        import asyncio
        asyncio.run(update_db())
        
        return {"success": True, "url": result["secure_url"]}
        
    except Exception as exc:
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

### Tâche Celery - Email SMTP (tasks/email_tasks.py)

```python
from celery import shared_task
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.logs import EmailLog

@shared_task(bind=True, max_retries=3)
def send_email(self, recipient: str, subject: str, html_content: str, template_name: str):
    """
    Envoie email via SMTP
    """
    try:
        # Créer message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = recipient
        
        # Ajouter HTML
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        # Envoyer via SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        # Logger succès
        async def log_email():
            async with AsyncSessionLocal() as session:
                log = EmailLog(
                    recipient_email=recipient,
                    subject=subject,
                    template_name=template_name,
                    status="sent"
                )
                session.add(log)
                await session.commit()
        
        import asyncio
        asyncio.run(log_email())
        
        return {"success": True}
        
    except Exception as exc:
        # Logger échec
        async def log_error():
            async with AsyncSessionLocal() as session:
                log = EmailLog(
                    recipient_email=recipient,
                    subject=subject,
                    template_name=template_name,
                    status="failed",
                    error_message=str(exc)
                )
                session.add(log)
                await session.commit()
        
        import asyncio
        asyncio.run(log_error())
        
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def send_verification_initiated_email(email: str, verification_id: str):
    """Email de démarrage de vérification"""
    html = f"""
    <html>
        <body>
            <h2>Vérification KYC initiée</h2>
            <p>Votre vérification d'identité a été initiée.</p>
            <p>Référence: {verification_id}</p>
        </body>
    </html>
    """
    return send_email(email, "Vérification KYC initiée", html, "verification_initiated")
```

### Tâche Celery - Webhooks (tasks/webhook_tasks.py)

```python
from celery import shared_task
import httpx
import hmac
import hashlib
from app.db.session import AsyncSessionLocal
from app.models.logs import WebhookLog

@shared_task(bind=True, max_retries=5)
def send_webhook(self, webhook_url: str, webhook_secret: str, payload: dict, 
                 verification_id: str, company_id: str, event_type: str):
    """
    Envoie webhook avec signature HMAC
    """
    try:
        # Créer signature
        payload_str = str(payload)
        signature = hmac.new(
            webhook_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Headers avec signature
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Event-Type": event_type
        }
        
        # Envoyer webhook (timeout 10s)
        response = httpx.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=10.0
        )
        
        # Logger
        async def log_webhook():
            async with AsyncSessionLocal() as session:
                log = WebhookLog(
                    verification_id=verification_id,
                    company_id=company_id,
                    event_type=event_type,
                    webhook_url=webhook_url,
                    payload=payload,
                    response_status=response.status_code,
                    response_body=response.text[:1000],
                    success=response.status_code == 200,
                    retry_count=self.request.retries
                )
                session.add(log)
                await session.commit()
        
        import asyncio
        asyncio.run(log_webhook())
        
        if response.status_code != 200:
            raise Exception(f"Webhook failed with status {response.status_code}")
        
        return {"success": True}
        
    except Exception as exc:
        # Retry avec backoff: 1min, 5min, 15min, 30min, 1h
        countdown = [60, 300, 900, 1800, 3600][min(self.request.retries, 4)]
        raise self.retry(exc=exc, countdown=countdown)
```

---

## 🎨 Architecture Frontend Next.js

### Structure du projet

```
frontend/
├── src/
│   ├── app/                    # App Router (Next.js 13+)
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   │
│   │   ├── (auth)/             # Routes authentification
│   │   │   ├── login/
│   │   │   └── register/
│   │   │
│   │   ├── dashboard/          # Dashboard entreprise
│   │   │   ├── page.tsx
│   │   │   ├── verifications/
│   │   │   ├── statistics/
│   │   │   ├── api-keys/
│   │   │   └── settings/
│   │   │
│   │   ├── admin/              # Dashboard admin
│   │   │   ├── page.tsx
│   │   │   ├── companies/
│   │   │   ├── verifications/
│   │   │   └── review/
│   │   │
│   │   └── session/            # Page vérification utilisateur
│   │       └── [token]/
│   │           └── page.tsx
│   │
│   ├── components/             # Composants réutilisables
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── forms/
│   │   ├── tables/
│   │   └── charts/
│   │
│   ├── lib/                    # Utilitaires
│   │   ├── api.ts              # Client API
│   │   ├── auth.ts             # Gestion auth
│   │   └── utils.ts
│   │
│   ├── hooks/                  # Custom hooks
│   │   ├── useVerifications.ts
│   │   └── useAuth.ts
│   │
│   └── types/                  # TypeScript types
│       └── index.ts
│
├── public/
├── package.json
└── tailwind.config.js
```

### Technologies Frontend

- **Framework** : Next.js 14+ (App Router)
- **UI** : shadcn/ui + Radix UI
- **Styling** : TailwindCSS
- **Icons** : Lucide React
- **Forms** : React Hook Form + Zod
- **State** : Zustand ou React Query
- **Charts** : Recharts
- **Tables** : TanStack Table

### Page de vérification utilisateur (session/[token]/page.tsx)

```typescript
'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';

export default function VerificationPage() {
  const { token } = useParams();
  const [step, setStep] = useState(1);
  
  // Étapes: 1=Identité, 2=Document, 3=Selfie, 4=Confirmation
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="max-w-2xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-6">Vérification d'identité</h1>
        
        {/* Stepper */}
        <div className="flex justify-between mb-8">
          {[1, 2, 3, 4].map(s => (
            <div key={s} className={`flex-1 h-2 rounded ${s <= step ? 'bg-blue-600' : 'bg-gray-200'}`} />
          ))}
        </div>
        
        {/* Contenu selon étape */}
        {step === 1 && <IdentityStep onNext={() => setStep(2)} />}
        {step === 2 && <DocumentStep onNext={() => setStep(3)} />}
        {step === 3 && <SelfieStep onNext={() => setStep(4)} />}
        {step === 4 && <ConfirmationStep />}
      </Card>
    </div>
  );
}
```

---

## 🔐 Sécurité & Authentification

### JWT pour entreprises

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    """Vérifie la clé API secrète"""
    secret_key = credentials.credentials
    
    # Chercher entreprise avec cette clé
    result = await db.execute(
        select(Company).where(Company.secret_key == secret_key)
    )
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=401, detail="Clé API invalide")
    
    if company.status == "suspended":
        raise HTTPException(status_code=403, detail="Compte suspendu")
    
    return company
```

### Rate Limiting avec Redis

```python
# core/rate_limiter.py
import redis
from fastapi import HTTPException, Request
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

async def check_rate_limit(request: Request, company_id: str):
    """Limite à 60 requêtes/minute par entreprise"""
    key = f"rate_limit:{company_id}:{int(time.time() / 60)}"
    
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    
    if current > settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Trop de requêtes")
    
    return True
```

---

## 📦 Déploiement & Infrastructure

### Docker Compose (Production)

```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: kyc_platform
      POSTGRES_USER: kyc_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  # Backend FastAPI
  backend:
    build: ./backend
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    environment:
      DATABASE_URL: postgresql://kyc_user:${DB_PASSWORD}@postgres:5432/kyc_platform
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
  
  # Celery Worker
  celery_worker:
    build: ./backend
    command: celery -A celery_app worker --loglevel=info --concurrency=4
    environment:
      DATABASE_URL: postgresql://kyc_user:${DB_PASSWORD}@postgres:5432/kyc_platform
      REDIS_URL: redis://redis:6379/0
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on:
      - postgres
      - redis
  
  # Frontend Next.js
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### Requirements.txt (Backend)

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
gunicorn==21.2.0
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
celery==5.3.6
redis==5.0.1
cloudinary==1.38.0
Pillow==10.2.0
httpx==0.26.0
slowapi==0.1.9
python-dotenv==1.0.0
```

---

## 📈 Monitoring & Performance

### Métriques à surveiller

1. **Performance API**
   - Temps de réponse moyen
   - Requêtes/seconde
   - Taux d'erreur

2. **Celery Tasks**
   - Tâches en attente
   - Tâches échouées
   - Temps d'exécution moyen

3. **Base de données**
   - Connexions actives
   - Requêtes lentes
   - Taille DB

4. **Redis**
   - Mémoire utilisée
   - Hit rate cache
   - Connexions

### Outils recommandés

- **Monitoring** : Prometheus + Grafana
- **Logs** : ELK Stack (Elasticsearch, Logstash, Kibana)
- **APM** : Sentry pour erreurs
- **Uptime** : UptimeRobot

---

## 🚀 Phases de Développement

### Phase 1 : Infrastructure (2-3 semaines)
- ✅ Setup PostgreSQL + migrations Alembic
- ✅ Configuration FastAPI + structure projet
- ✅ Setup Redis + Celery
- ✅ Authentification JWT
- ✅ Rate limiting

### Phase 2 : API Core (3-4 semaines)
- ✅ Endpoints vérification (initiate, status, list)
- ✅ Gestion entreprises (CRUD)
- ✅ Système de webhooks
- ✅ Logs API
- ✅ Tests unitaires

### Phase 3 : Background Tasks (2 semaines)
- ✅ Compression images Celery
- ✅ Upload Cloudinary
- ✅ Emails SMTP
- ✅ Webhooks async
- ✅ Retry logic

### Phase 4 : Frontend Dashboard Entreprise (3 semaines)
- ✅ Interface Next.js
- ✅ Authentification
- ✅ Liste vérifications
- ✅ Statistiques
- ✅ Gestion API keys

### Phase 5 : Frontend Vérification Utilisateur (2 semaines)
- ✅ Page session unique
- ✅ Upload documents
- ✅ Capture selfie
- ✅ Validation formulaire

### Phase 6 : Dashboard Admin (2-3 semaines)
- ✅ Gestion entreprises
- ✅ Validation manuelle KYC
- ✅ Visualisation documents
- ✅ Statistiques globales

### Phase 7 : Sécurité & Optimisation (2 semaines)
- ✅ Détection doublons
- ✅ Blacklist
- ✅ Optimisation requêtes DB
- ✅ Cache Redis stratégique
- ✅ Tests de charge

### Phase 8 : Documentation & Déploiement (1-2 semaines)
- ✅ Documentation API (Swagger)
- ✅ Guide intégration
- ✅ Exemples code (Flutter, Next.js, Laravel)
- ✅ Déploiement production
- ✅ Monitoring

**Durée totale estimée : 17-21 semaines (4-5 mois)**

---

## 📚 Documentation API

### Exemple d'intégration

#### Python (FastAPI/Flask)
```python
import httpx

API_URL = "https://api.votredomaine.com/api/v1"
SECRET_KEY = "votre_cle_secrete"

async def initiate_kyc(full_name: str, email: str):
    headers = {"Authorization": f"Bearer {SECRET_KEY}"}
    payload = {
        "full_name": full_name,
        "email": email,
        "external_reference": "REF-12345"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/verifications/initiate",
            json=payload,
            headers=headers
        )
        return response.json()

# Résultat
# {
#   "verification_id": "KYC-20260001",
#   "verification_url": "https://verification.votredomaine.com/session/abc123",
#   "status": "pending"
# }
```

#### JavaScript (Next.js)
```javascript
const API_URL = 'https://api.votredomaine.com/api/v1';
const SECRET_KEY = 'votre_cle_secrete';

async function initiateKYC(fullName, email) {
  const response = await fetch(`${API_URL}/verifications/initiate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${SECRET_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      full_name: fullName,
      email: email,
      external_reference: 'REF-12345'
    })
  });
  
  return await response.json();
}
```

#### Flutter (Dart)
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

const String apiUrl = 'https://api.votredomaine.com/api/v1';
const String secretKey = 'votre_cle_secrete';

Future<Map<String, dynamic>> initiateKYC(String fullName, String email) async {
  final response = await http.post(
    Uri.parse('$apiUrl/verifications/initiate'),
    headers: {
      'Authorization': 'Bearer $secretKey',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({
      'full_name': fullName,
      'email': email,
      'external_reference': 'REF-12345',
    }),
  );
  
  return jsonDecode(response.body);
}
```

---

## ✅ Checklist Finale

### Backend
- [ ] FastAPI configuré avec async/await
- [ ] PostgreSQL + asyncpg + SQLAlchemy async
- [ ] Redis pour cache et rate limiting
- [ ] Celery pour tâches background
- [ ] Compression images avant upload
- [ ] Cloudinary intégré
- [ ] SMTP emails avec retry
- [ ] Webhooks avec signature HMAC
- [ ] JWT authentication
- [ ] Rate limiting par entreprise
- [ ] Logs complets (API, webhooks, emails)
- [ ] Détection doublons
- [ ] Blacklist système
- [ ] Tests unitaires

### Frontend
- [ ] Next.js 14+ App Router
- [ ] Dashboard entreprise responsive
- [ ] Dashboard admin
- [ ] Page vérification utilisateur
- [ ] Upload fichiers avec preview
- [ ] Statistiques avec charts
- [ ] Gestion API keys
- [ ] Dark mode (optionnel)

### Infrastructure
- [ ] Docker Compose production
- [ ] Gunicorn + Uvicorn workers
- [ ] Celery workers configurés
- [ ] Redis persistant
- [ ] PostgreSQL avec backups
- [ ] SSL/TLS certificats
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Logs centralisés

### Sécurité
- [ ] Variables d'environnement sécurisées
- [ ] Clés API uniques par entreprise
- [ ] Webhook signatures
- [ ] Rate limiting actif
- [ ] Expiration sessions
- [ ] Chiffrement données sensibles
- [ ] CORS configuré
- [ ] Protection CSRF

### Documentation
- [ ] Swagger/OpenAPI auto-généré
- [ ] Guide intégration développeurs
- [ ] Exemples code (Python, JS, Flutter, PHP)
- [ ] Documentation webhooks
- [ ] Guide sandbox vs production
- [ ] FAQ

---

## 🎯 Recommandations Finales

### Performance
1. **Toujours utiliser async/await** pour IO-bound operations
2. **Jamais bloquer la requête principale** - tout en background
3. **Indexer toutes les colonnes** utilisées dans WHERE/JOIN
4. **Pagination obligatoire** - max 20-50 résultats
5. **Cache Redis** pour statistiques et quotas
6. **Cloudinary transformations** au lieu de compression locale

### Scalabilité
1. **Séparer services** si volume augmente (API, Workers, DB)
2. **Load balancer** pour backend (Nginx/HAProxy)
3. **Read replicas** PostgreSQL pour lectures
4. **CDN** pour assets statiques
5. **Horizontal scaling** Celery workers

### Maintenance
1. **Logs structurés** (JSON) pour parsing facile
2. **Monitoring alertes** sur métriques critiques
3. **Backups automatiques** DB quotidiens
4. **Tests automatisés** CI/CD
5. **Documentation à jour** avec chaque feature

---

**Ce plan technique couvre tous les aspects du cahier des charges avec une architecture moderne, performante et scalable. Prêt pour démarrage du développement ! 🚀**
