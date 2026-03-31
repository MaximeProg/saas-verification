from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.config import settings
from app.db.session import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    print("🚀 Démarrage de l'application KYC Platform...")
    
    # Créer les tables si elles n'existent pas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Base de données initialisée")
    
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Plateforme SaaS de vérification d'identité (KYC)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "KYC Platform API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


# Import des routes
from app.api.v1 import verifications, companies, admin, session
from app.api.v1.endpoints import subscription_plans, payments

app.include_router(
    verifications.router,
    prefix=f"{settings.API_V1_PREFIX}/verifications",
    tags=["Verifications"]
)
app.include_router(
    companies.router,
    prefix=f"{settings.API_V1_PREFIX}/companies",
    tags=["Companies"]
)
app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin"]
)
app.include_router(
    session.router,
    prefix=f"{settings.API_V1_PREFIX}/session",
    tags=["Session"]
)
app.include_router(
    subscription_plans.router,
    prefix=f"{settings.API_V1_PREFIX}/subscription-plans",
    tags=["Subscription Plans"]
)
app.include_router(
    payments.router,
    prefix=f"{settings.API_V1_PREFIX}/payments",
    tags=["Payments"]
)

# Créer le dossier uploads s'il n'existe pas
upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)

# Servir les fichiers statiques
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
