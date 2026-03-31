from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

# Créer le moteur async avec asyncpg pour Neon PostgreSQL
engine = create_async_engine(
    settings.database_url_asyncpg,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    pool_recycle=3600,   # Recycler les connexions après 1h
    connect_args={"ssl": "require"}  # SSL requis pour Neon
)

# Session factory async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """Dependency pour obtenir une session de base de données"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
