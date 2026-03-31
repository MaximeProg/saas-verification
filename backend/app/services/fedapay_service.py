"""
Service d'intégration FedaPay pour les paiements
"""
import httpx
from typing import Optional, Dict, Any
from app.config import settings


class FedaPayService:
    """Service pour gérer les paiements via FedaPay"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'FEDAPAY_API_KEY', None)
        self.api_secret = getattr(settings, 'FEDAPAY_API_SECRET', None)
        self.base_url = getattr(settings, 'FEDAPAY_BASE_URL', 'https://api.fedapay.com/v1')
        self.environment = getattr(settings, 'FEDAPAY_ENVIRONMENT', 'sandbox')
    
    async def create_transaction(
        self,
        amount: float,
        currency: str,
        description: str,
        customer_email: str,
        customer_name: str,
        callback_url: str,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Créer une transaction FedaPay
        
        Args:
            amount: Montant en FCFA
            currency: Devise (XOF)
            description: Description de la transaction
            customer_email: Email du client
            customer_name: Nom du client
            callback_url: URL de callback après paiement
            custom_metadata: Métadonnées personnalisées
        
        Returns:
            Dict contenant les détails de la transaction et l'URL de paiement
        """
        
        if not self.api_key or not self.api_secret:
            raise ValueError("FedaPay API credentials not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "amount": int(amount),
            "currency": {
                "iso": currency
            },
            "description": description,
            "callback_url": callback_url,
            "customer": {
                "email": customer_email,
                "firstname": customer_name.split()[0] if customer_name else "",
                "lastname": " ".join(customer_name.split()[1:]) if len(customer_name.split()) > 1 else ""
            }
        }
        
        if custom_metadata:
            payload["custom_metadata"] = custom_metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/transactions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
        
        return {
            "transaction_id": data.get("v1/transaction", {}).get("id"),
            "payment_url": data.get("v1/transaction", {}).get("url"),
            "status": data.get("v1/transaction", {}).get("status"),
            "amount": data.get("v1/transaction", {}).get("amount"),
            "currency": data.get("v1/transaction", {}).get("currency", {}).get("iso"),
            "reference": data.get("v1/transaction", {}).get("reference")
        }
    
    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Récupérer le statut d'une transaction
        
        Args:
            transaction_id: ID de la transaction FedaPay
        
        Returns:
            Dict contenant les détails de la transaction
        """
        
        if not self.api_key:
            raise ValueError("FedaPay API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/transactions/{transaction_id}",
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
        
        transaction = data.get("v1/transaction", {})
        
        return {
            "transaction_id": transaction.get("id"),
            "status": transaction.get("status"),
            "amount": transaction.get("amount"),
            "currency": transaction.get("currency", {}).get("iso"),
            "reference": transaction.get("reference"),
            "approved_at": transaction.get("approved_at"),
            "customer": transaction.get("customer")
        }
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Vérifier la signature d'un webhook FedaPay
        
        Args:
            payload: Corps de la requête webhook
            signature: Signature fournie dans les headers
        
        Returns:
            True si la signature est valide
        """
        import hmac
        import hashlib
        
        if not self.api_secret:
            raise ValueError("FedaPay API secret not configured")
        
        expected_signature = hmac.new(
            self.api_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
