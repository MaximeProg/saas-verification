"""
Service d'intégration FedaPay pour les paiements
Documentation: https://docs.fedapay.com
"""
import requests
from typing import Optional, Dict
from datetime import datetime, timedelta
import json

from app.config import settings


class FedaPayService:
    """Service pour gérer les paiements via FedaPay"""
    
    def __init__(self):
        self.api_key = settings.FEDAPAY_API_KEY
        self.environment = settings.FEDAPAY_ENVIRONMENT  # "sandbox" ou "live"
        self.base_url = self._get_base_url()
        self.simulation_mode = not self.api_key  # Mode simulation si pas de clé API
        
    def _get_base_url(self) -> str:
        """Retourne l'URL de base selon l'environnement"""
        if self.environment == "sandbox":
            return "https://sandbox-api.fedapay.com/v1"
        return "https://api.fedapay.com/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Retourne les headers pour les requêtes API"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_transaction(
        self,
        amount: float,
        currency: str,
        description: str,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Créer une transaction FedaPay
        
        Args:
            amount: Montant en FCFA
            currency: Devise (XOF, XAF, etc.)
            description: Description du paiement
            customer_email: Email du client
            customer_phone: Téléphone du client
            callback_url: URL de callback après paiement
            metadata: Données supplémentaires
        
        Returns:
            Dict contenant les informations de la transaction
        """
        endpoint = f"{self.base_url}/transactions"
        
        payload = {
            "amount": int(amount),  # FedaPay attend un entier
            "currency": {
                "iso": currency
            },
            "description": description,
        }
        
        # Ajouter les informations client si fournies
        if customer_email or customer_phone:
            payload["customer"] = {}
            if customer_email:
                payload["customer"]["email"] = customer_email
                # Extraire le nom depuis l'email si pas fourni autrement
                email_name = customer_email.split('@')[0]
                payload["customer"]["firstname"] = email_name.split('.')[0].capitalize() if '.' in email_name else email_name.capitalize()
                payload["customer"]["lastname"] = email_name.split('.')[1].capitalize() if '.' in email_name and len(email_name.split('.')) > 1 else "Client"
            if customer_phone:
                payload["customer"]["phone_number"] = {
                    "number": customer_phone,
                    "country": "bj"  # Bénin par défaut, à adapter
                }
        
        # Ajouter callback URL
        if callback_url:
            payload["callback_url"] = callback_url
        
        # Ajouter métadonnées
        if metadata:
            payload["metadata"] = metadata
        
        # Mode simulation si pas de clé API
        if self.simulation_mode:
            import uuid
            fake_token = f"sim_{uuid.uuid4().hex[:16]}"
            return {
                "success": True,
                "transaction_id": f"sim_txn_{uuid.uuid4().hex[:12]}",
                "token": fake_token,
                "status": "pending",
                "payment_url": f"http://localhost:3000/payment/simulation/{fake_token}",
                "data": {"simulation": True}
            }
        
        try:
            # Log du payload pour debug
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"FedaPay payload: {payload}")
            
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            transaction = data.get("v1/transaction", {})
            return {
                "success": True,
                "transaction_id": transaction.get("id"),
                "token": transaction.get("payment_token"),
                "status": transaction.get("status"),
                "payment_url": transaction.get("payment_url"),
                "data": data
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def _get_payment_url(self, token: str) -> str:
        """Génère l'URL de paiement FedaPay"""
        if self.environment == "sandbox":
            return f"https://sandbox-checkout.fedapay.com/{token}"
        return f"https://checkout.fedapay.com/{token}"
    
    def get_transaction(self, transaction_id: str) -> Dict:
        """
        Récupérer les détails d'une transaction
        
        Args:
            transaction_id: ID de la transaction FedaPay
        
        Returns:
            Dict contenant les informations de la transaction
        """
        endpoint = f"{self.base_url}/transactions/{transaction_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            transaction = data.get("v1/transaction", {})
            
            return {
                "success": True,
                "transaction_id": transaction.get("id"),
                "status": transaction.get("status"),
                "amount": transaction.get("amount"),
                "currency": transaction.get("currency", {}).get("iso"),
                "description": transaction.get("description"),
                "created_at": transaction.get("created_at"),
                "updated_at": transaction.get("updated_at"),
                "data": data
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def verify_transaction(self, transaction_id: str) -> bool:
        """
        Vérifier si une transaction est complétée
        
        Args:
            transaction_id: ID de la transaction FedaPay
        
        Returns:
            True si la transaction est complétée, False sinon
        """
        result = self.get_transaction(transaction_id)
        
        if not result.get("success"):
            return False
        
        status = result.get("status")
        return status == "approved" or status == "completed"
    
    def process_webhook(self, payload: Dict, signature: str) -> Dict:
        """
        Traiter un webhook FedaPay
        
        Args:
            payload: Données du webhook
            signature: Signature du webhook
        
        Returns:
            Dict contenant les informations traitées
        """
        # TODO: Vérifier la signature du webhook
        # FedaPay envoie une signature HMAC dans les headers
        
        event_type = payload.get("event")
        transaction = payload.get("entity", {})
        
        return {
            "event_type": event_type,
            "transaction_id": transaction.get("id"),
            "status": transaction.get("status"),
            "amount": transaction.get("amount"),
            "currency": transaction.get("currency", {}).get("iso"),
            "customer_email": transaction.get("customer", {}).get("email"),
            "metadata": transaction.get("metadata", {})
        }


# Instance globale du service
fedapay_service = FedaPayService()
