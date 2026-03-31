from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Application
    APP_NAME: str = "KYC Platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database Neon PostgreSQL
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    @property
    def database_url_asyncpg(self) -> str:
        """Convertit l'URL Neon pour asyncpg (retire sslmode et channel_binding)"""
        url = self.DATABASE_URL
        # Retirer les paramètres incompatibles avec asyncpg
        if "?" in url:
            base_url = url.split("?")[0]
            return base_url
        return url
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # JWT Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # SMTP
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Session
    SESSION_EXPIRE_HOURS: int = 48
    VERIFICATION_URL_BASE: str = "http://localhost:3000/session"
    
    # Storage
    UPLOAD_DIR: str = "uploads"
    STORAGE_URL_BASE: str = "http://localhost:8000/uploads"
    
    # FedaPay Configuration
    FEDAPAY_API_KEY: Optional[str] = None
    FEDAPAY_API_SECRET: Optional[str] = None
    FEDAPAY_WEBHOOK_SECRET: Optional[str] = None
    FEDAPAY_BASE_URL: str = "https://api.fedapay.com/v1"
    FEDAPAY_ENVIRONMENT: str = "sandbox"  # sandbox ou live
    FEDAPAY_CALLBACK_URL: str = "http://localhost:8000/api/v1/payments/fedapay/callback"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
