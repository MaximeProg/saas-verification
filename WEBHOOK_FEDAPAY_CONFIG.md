# Configuration Webhook FedaPay

## 📋 URL du Webhook

Pour que les paiements soient automatiquement mis à jour après validation sur FedaPay, configurez le webhook dans votre dashboard FedaPay.

### **URL à configurer**

```
https://votre-domaine.com/api/v1/payments/webhook
```

**En développement local** :
```
http://localhost:8000/api/v1/payments/webhook
```

**Note** : Pour tester en local, utilisez un service comme **ngrok** pour exposer votre backend :
```bash
ngrok http 8000
# Utilisez l'URL fournie par ngrok : https://xxxx.ngrok.io/api/v1/payments/webhook
```

---

## 🔧 Configuration dans FedaPay Dashboard

1. **Connectez-vous** à [https://dashboard.fedapay.com](https://dashboard.fedapay.com)
2. Allez dans **Paramètres** → **Webhooks**
3. Cliquez sur **Ajouter un webhook**
4. **URL du webhook** : `https://votre-domaine.com/api/v1/payments/webhook`
5. **Événements à écouter** :
   - ✅ `transaction.approved`
   - ✅ `transaction.completed`
   - ✅ `transaction.failed`
   - ✅ `transaction.cancelled`
6. Cliquez sur **Enregistrer**

---

## 🔐 Sécurité (Optionnel)

Le webhook vérifie la signature FedaPay pour s'assurer que les requêtes proviennent bien de FedaPay.

**Variable d'environnement** dans `backend/.env` :
```env
FEDAPAY_WEBHOOK_SECRET=votre_secret_webhook
```

---

## 📊 Workflow de mise à jour automatique

### **Flux complet**

```
1. Utilisateur clique "Choisir ce plan"
   ↓
2. Modal FedaPay s'ouvre (iframe intégré)
   ↓
3. Utilisateur effectue le paiement sur FedaPay
   ↓
4. FedaPay envoie webhook → /api/v1/payments/webhook
   ↓
5. Backend met à jour :
   - payment.status = "completed"
   - payment.paid_at = now()
   - company.subscription_plan = plan.name
   - company.monthly_quota = plan.monthly_quota
   - company.subscription_expires_at = now() + 30 jours
   ↓
6. Utilisateur ferme le modal
   ↓
7. Page se recharge → Abonnement actif affiché ✅
```

---

## 🔄 Vérification manuelle

Si le webhook ne fonctionne pas (problème de configuration, firewall, etc.), l'utilisateur peut **vérifier manuellement** le statut :

1. Dans l'historique des paiements
2. Cliquez sur le bouton **"Vérifier"** à côté d'un paiement "En cours"
3. Le système interroge directement l'API FedaPay
4. Si le paiement est validé → mise à jour automatique

**Endpoint utilisé** : `POST /api/v1/payments/{payment_id}/verify`

---

## 🧪 Test du webhook

### **Tester avec ngrok (développement local)**

```bash
# Terminal 1 : Démarrer le backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2 : Exposer avec ngrok
ngrok http 8000

# Copier l'URL ngrok (ex: https://abc123.ngrok.io)
# Configurer dans FedaPay : https://abc123.ngrok.io/api/v1/payments/webhook
```

### **Simuler un webhook manuellement**

```bash
curl -X POST http://localhost:8000/api/v1/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "transaction",
    "event": "transaction.approved",
    "transaction": {
      "id": 12345,
      "status": "approved",
      "amount": 10000,
      "currency": "XOF",
      "metadata": {
        "payment_id": "uuid-du-paiement",
        "company_id": "uuid-de-la-company"
      }
    }
  }'
```

---

## ⚠️ Problèmes courants

### **1. Webhook non reçu**
- ✅ Vérifiez que l'URL est accessible publiquement
- ✅ Vérifiez les logs backend pour voir si la requête arrive
- ✅ Utilisez ngrok en développement local

### **2. Paiement validé mais statut "En cours"**
- ✅ Cliquez sur le bouton **"Vérifier"** dans l'historique
- ✅ Vérifiez les logs backend : `INFO: Webhook received`
- ✅ Vérifiez que `FEDAPAY_API_KEY` est correcte dans `.env`

### **3. Abonnement non activé après paiement**
- ✅ Vérifiez que le webhook a bien été reçu
- ✅ Vérifiez les logs : `INFO: Payment updated to completed`
- ✅ Actualisez la page `/company/dashboard/subscription`

---

## 📝 Logs à surveiller

Dans les logs backend, vous devriez voir :

```
INFO: Webhook received from FedaPay
INFO: Payment PAY-20260323-XXXX updated to completed
INFO: Company subscription activated: starter plan
```

Si vous ne voyez pas ces logs après un paiement, le webhook n'est pas configuré correctement.

---

## 🎯 Résumé

| Élément | Valeur |
|---------|--------|
| **URL Webhook** | `https://votre-domaine.com/api/v1/payments/webhook` |
| **Méthode** | POST |
| **Authentification** | Signature FedaPay (optionnel) |
| **Événements** | `transaction.approved`, `transaction.completed` |
| **Vérification manuelle** | Bouton "Vérifier" dans l'historique |

---

**Besoin d'aide ?** Consultez la documentation FedaPay : [https://docs.fedapay.com/webhooks](https://docs.fedapay.com/webhooks)
