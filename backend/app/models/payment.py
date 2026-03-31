from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


class PaymentStatus(str, enum.Enum):
    """Statuts de paiement"""
    PENDING = "pending"  # En attente
    PROCESSING = "processing"  # En cours de traitement
    COMPLETED = "completed"  # Complété
    FAILED = "failed"  # Échoué
    REFUNDED = "refunded"  # Remboursé
    CANCELLED = "cancelled"  # Annulé


class PaymentMethod(str, enum.Enum):
    """Méthodes de paiement FedaPay"""
    MOBILE_MONEY = "mobile_money"  # Mobile Money (MTN, Moov, etc.)
    CARD = "card"  # Carte bancaire
    BANK_TRANSFER = "bank_transfer"  # Virement bancaire


class Payment(Base):
    """Modèle pour les paiements"""
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Référence unique
    payment_reference = Column(String(100), unique=True, nullable=False)  # Ex: PAY-2026-000001
    
    # Entreprise
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="payments")
    
    # Plan d'abonnement
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    plan = relationship("SubscriptionPlan")
    
    # Montant
    amount = Column(Float, nullable=False)  # Montant en FCFA
    currency = Column(String(3), default="XOF")
    
    # FedaPay
    fedapay_transaction_id = Column(String(255), unique=True)  # ID transaction FedaPay
    fedapay_token = Column(String(255))  # Token FedaPay
    fedapay_status = Column(String(50))  # Statut FedaPay
    fedapay_response = Column(Text)  # Réponse complète FedaPay (JSON)
    
    # Méthode de paiement
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    
    # Statut
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)  # Date de paiement effectif
    expires_at = Column(DateTime)  # Date d'expiration du lien de paiement
    
    # Informations supplémentaires
    description = Column(Text)  # Description du paiement
    customer_email = Column(String(255))  # Email du client
    customer_phone = Column(String(20))  # Téléphone du client
    
    # Callback URLs
    callback_url = Column(String(500))  # URL de callback après paiement
    return_url = Column(String(500))  # URL de retour après paiement
    
    # Métadonnées
    payment_metadata = Column(Text)  # Données supplémentaires (JSON)
    
    def __repr__(self):
        return f"<Payment {self.payment_reference} - {self.amount} {self.currency} - {self.status}>"
