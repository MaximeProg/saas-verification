from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.base import Base


class SubscriptionPlan(Base):
    """Modèle pour les plans d'abonnement"""
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Informations du plan
    name = Column(String(100), nullable=False, unique=True)  # Ex: "Starter", "Professional", "Enterprise"
    slug = Column(String(50), nullable=False, unique=True)  # Ex: "starter", "professional"
    description = Column(Text, nullable=False)
    
    # Tarification
    price = Column(Float, nullable=False)  # Prix en FCFA
    currency = Column(String(3), default="XOF")  # XOF (Franc CFA)
    billing_period = Column(String(20), default="monthly")  # monthly, yearly
    
    # Quotas et limites
    monthly_quota = Column(Integer, nullable=False)  # Nombre de vérifications/mois
    max_api_keys = Column(Integer, default=5)  # Nombre max de clés API
    max_users = Column(Integer, default=1)  # Nombre max d'utilisateurs
    
    # Fonctionnalités
    features = Column(JSON, nullable=False)  # Liste des fonctionnalités
    # Exemple: {
    #   "webhook_support": true,
    #   "priority_support": false,
    #   "custom_branding": false,
    #   "api_access": true,
    #   "bulk_upload": false,
    #   "advanced_analytics": false
    # }
    
    # Avantages (pour affichage)
    advantages = Column(JSON, nullable=False)  # Liste des avantages
    # Exemple: [
    #   "100 vérifications par mois",
    #   "Support email",
    #   "Webhooks inclus",
    #   "API REST complète"
    # ]
    
    # Statut
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)  # Badge "Populaire"
    is_custom = Column(Boolean, default=False)  # Plan personnalisé
    
    # Ordre d'affichage
    display_order = Column(Integer, default=0)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))  # Admin qui a créé le plan
    
    def __repr__(self):
        return f"<SubscriptionPlan {self.name} - {self.price} {self.currency}/{self.billing_period}>"
