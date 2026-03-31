# 🔗 Configuration Webhook FedaPay

## 📍 URL du Webhook

Votre URL de webhook FedaPay est :

```
https://votre-domaine.com/api/v1/payments/webhook
```

**Exemples selon votre déploiement** :

### Si déployé sur Render
```
https://kyc-platform-api.onrender.com/api/v1/payments/webhook
```

### Si déployé sur Vercel/Netlify
```
https://api.votre-domaine.com/api/v1/payments/webhook
```

### Pour tests en local (avec ngrok)
```
https://abc123.ngrok.io/api/v1/payments/webhook
```

---

## ⚙️ Configuration sur FedaPay Dashboard

### Étape 1 : Se Connecter
1. Aller sur : https://dashboard.fedapay.com
2. Se connecter avec vos identifiants

### Étape 2 : Accéder aux Webhooks
1. Menu latéral → **Développeurs** ou **Developers**
2. Cliquer sur **Webhooks**

### Étape 3 : Ajouter le Webhook
1. Cliquer sur **+ Ajouter un webhook** ou **+ Add webhook**
2. Remplir les informations :

```
URL du webhook : https://votre-domaine.com/api/v1/payments/webhook
Description : KYC Platform - Notifications de paiement
```

### Étape 4 : Sélectionner les Événements

Cocher ces événements :

- ✅ `transaction.approved` - Transaction approuvée
- ✅ `transaction.completed` - Transaction complétée
- ✅ `transaction.failed` - Transaction échouée
- ✅ `transaction.cancelled` - Transaction annulée

### Étape 5 : Sauvegarder

1. Cliquer sur **Créer** ou **Create**
2. **Copier le Webhook Secret** qui s'affiche
3. Le sauvegarder dans votre `.env`

---

## 🔐 Configuration .env (Mode LIVE)

Puisque votre compte est en **mode live**, voici la configuration :

```env
# FedaPay - MODE LIVE (PRODUCTION)
FEDAPAY_API_KEY=sk_live_VOTRE_CLE_API_LIVE
FEDAPAY_ENVIRONMENT=live
FEDAPAY_WEBHOOK_SECRET=whsec_VOTRE_SECRET_WEBHOOK
```

### Où trouver vos clés ?

1. **Dashboard FedaPay** → **Développeurs** → **Clés API**
2. Copier :
   - **Secret Key (Live)** : `sk_live_...`
   - **Public Key (Live)** : `pk_live_...` (pour frontend si besoin)

---

## 🧪 Tester le Webhook

### Option 1 : Utiliser l'outil de test FedaPay

1. Dashboard FedaPay → Webhooks
2. Cliquer sur votre webhook
3. Cliquer **Tester** ou **Test**
4. FedaPay envoie un événement de test

### Option 2 : Faire un vrai paiement de test

1. Créer une transaction via l'API
2. Effectuer un paiement (petit montant)
3. Vérifier les logs de votre serveur

---

## 📊 Vérifier que le Webhook Fonctionne

### Dans les Logs de votre Serveur

Vous devriez voir :

```
POST /api/v1/payments/webhook
Status: 200 OK
Body: {"status": "success", "payment_id": "..."}
```

### Dans FedaPay Dashboard

1. Webhooks → Votre webhook
2. Onglet **Historique** ou **History**
3. Voir les événements envoyés et les réponses

**Statut 200** = ✅ Webhook reçu et traité  
**Statut 4xx/5xx** = ❌ Erreur à corriger

---

## 🔒 Sécurité du Webhook

Le webhook vérifie automatiquement :

1. **Signature HMAC** (à implémenter si FedaPay l'envoie)
2. **Transaction ID** valide
3. **Payment ID** existe en DB

### Code de Vérification (déjà implémenté)

```python
# app/api/v1/endpoints/payments.py
@router.post("/webhook")
async def fedapay_webhook(request: Request, db: AsyncSession):
    payload = await request.json()
    signature = request.headers.get("X-FedaPay-Signature", "")
    
    # Traiter le webhook
    webhook_data = fedapay_service.process_webhook(payload, signature)
    
    # Mettre à jour le paiement
    # Activer l'abonnement si paiement complété
    ...
```

---

## 🚨 Dépannage

### Le webhook ne reçoit rien

1. **Vérifier l'URL** : Doit être accessible publiquement (pas localhost)
2. **Vérifier le SSL** : FedaPay nécessite HTTPS
3. **Vérifier les logs** : Regarder les erreurs serveur

### Erreur 401/403

- Vérifier que l'endpoint `/payments/webhook` est **public** (pas d'authentification requise)

### Erreur 500

- Vérifier les logs serveur
- Vérifier que la DB est accessible
- Vérifier que les modèles `Payment` et `Company` sont corrects

---

## 📝 Exemple de Payload FedaPay

Voici ce que FedaPay envoie :

```json
{
  "event": "transaction.approved",
  "entity": {
    "id": "fedapay-transaction-id",
    "status": "approved",
    "amount": 50000,
    "currency": {
      "iso": "XOF"
    },
    "description": "Abonnement Professional - monthly",
    "customer": {
      "email": "client@example.com",
      "phone_number": {
        "number": "+22997123456",
        "country": "bj"
      }
    },
    "metadata": {
      "payment_id": "uuid-de-votre-paiement",
      "payment_reference": "PAY-20260314-ABCD1234",
      "company_id": "uuid-entreprise",
      "plan_id": "uuid-plan"
    },
    "created_at": "2026-03-14T20:00:00Z",
    "updated_at": "2026-03-14T20:05:00Z"
  }
}
```

---

## ✅ Checklist Configuration

- [ ] Obtenir clés API Live de FedaPay
- [ ] Ajouter `FEDAPAY_API_KEY` dans `.env`
- [ ] Mettre `FEDAPAY_ENVIRONMENT=live` dans `.env`
- [ ] Configurer webhook sur FedaPay Dashboard
- [ ] Copier `FEDAPAY_WEBHOOK_SECRET` dans `.env`
- [ ] Redémarrer le serveur
- [ ] Tester avec un paiement réel (petit montant)
- [ ] Vérifier dans Dashboard FedaPay que webhook reçoit 200 OK

---

## 🎯 Résumé Rapide

**URL Webhook** :
```
https://votre-domaine.com/api/v1/payments/webhook
```

**Configuration .env** :
```env
FEDAPAY_API_KEY=sk_live_...
FEDAPAY_ENVIRONMENT=live
FEDAPAY_WEBHOOK_SECRET=whsec_...
```

**Événements à activer** :
- transaction.approved
- transaction.completed
- transaction.failed
- transaction.cancelled

**Votre webhook est déjà codé et prêt dans** :
`app/api/v1/endpoints/payments.py` ligne 122-200
