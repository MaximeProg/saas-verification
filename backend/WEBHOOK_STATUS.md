# 🔗 État des Webhooks - Analyse Complète

## ✅ Ce qui Fonctionne

### 1. Infrastructure Webhook
- ✅ **Task Celery créée** : `send_verification_webhook`
- ✅ **Worker actif** : Task enregistrée et prête
- ✅ **Redis connecté** : Broker fonctionnel
- ✅ **Code implémenté** : Signature HMAC, retry, logs

### 2. Fonctionnalités Implémentées
- ✅ **Signature HMAC-SHA256** : Sécurité des webhooks
- ✅ **Retry automatique** : 5 tentatives avec backoff (5min → 80min)
- ✅ **Logs database** : Table `webhook_logs` avec tous les détails
- ✅ **Payload complet** : Toutes les données de vérification
- ✅ **Headers sécurisés** : X-Webhook-Signature

### 3. Intégration API
- ✅ Webhook lancé automatiquement lors de `POST /verifications/{id}/review`
- ✅ Events supportés :
  - `verification.pending`
  - `verification.in_review`
  - `verification.approved`
  - `verification.rejected`

---

## ⚠️ Limitation Actuelle

### Webhook URL Non Configurée
L'entreprise de test n'a **pas de webhook_url** configurée dans la DB.

**Résultat** : La task s'exécute mais retourne `{"success": false, "reason": "No webhook URL configured"}`

---

## ✅ Comment Tester les Webhooks

### Option 1 : Webhook.site (Recommandé pour tests)

**Étape 1** : Obtenir une URL de test
1. Ouvrir : https://webhook.site
2. Copier l'URL unique (ex: `https://webhook.site/abc-123-def`)

**Étape 2** : Configurer l'entreprise
```python
import asyncio
from sqlalchemy import update
from app.db.session import AsyncSessionLocal
from app.models.company import Company

async def set_webhook():
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(Company)
            .where(Company.company_name == "Test Company SAS")
            .values(webhook_url="https://webhook.site/votre-url-unique")
        )
        await db.commit()
        print("✅ Webhook URL configurée")

asyncio.run(set_webhook())
```

**Étape 3** : Tester
```bash
python test_webhook_simple.py
```

**Étape 4** : Vérifier
- Retourner sur webhook.site
- Vous devriez voir la requête POST avec :
  - Header `X-Webhook-Signature`
  - Body JSON avec les données de vérification

---

### Option 2 : Serveur Local de Test

**Créer un serveur webhook local** :
```python
# test_webhook_server.py
from flask import Flask, request
import hmac
import hashlib
import json

app = Flask(__name__)

WEBHOOK_SECRET = "votre_webhook_secret"  # De la DB

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.json
    
    # Vérifier signature
    payload_str = json.dumps(payload, sort_keys=True)
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if hmac.compare_digest(signature, expected):
        print(f"✅ Webhook reçu: {payload['event']}")
        print(f"   Verification: {payload['verification_id']}")
        print(f"   Status: {payload['status']}")
        return {'status': 'ok'}, 200
    else:
        print("❌ Signature invalide")
        return {'error': 'Invalid signature'}, 401

if __name__ == '__main__':
    app.run(port=5000)
```

Puis configurer : `webhook_url = "http://localhost:5000/webhook"`

---

### Option 3 : Via API Endpoint

**Configurer via l'API** :
```bash
# 1. Login entreprise
curl -X POST http://localhost:8000/api/v1/companies/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@company.com", "password": "password"}'

# 2. Configurer webhook (endpoint à créer)
curl -X POST http://localhost:8000/api/v1/companies/webhook \
  -H "Authorization: Bearer jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://webhook.site/abc-123"}'
```

---

## 📊 Payload Webhook Envoyé

```json
{
  "event": "verification.approved",
  "verification_id": "KYC-2026000001",
  "external_reference": "REF-001",
  "status": "approved",
  "full_name": "Jean Dupont",
  "email": "jean@example.com",
  "phone": "+33612345678",
  "country": "France",
  "document_type": "passport",
  "document_number": "12AB34567",
  "created_at": "2026-03-14T16:00:00",
  "completed_at": "2026-03-14T17:00:00",
  "rejection_reason": null,
  "timestamp": "2026-03-14T17:00:00"
}
```

**Header** :
```
X-Webhook-Signature: abc123def456...
```

---

## 🔐 Vérification Signature (Côté Entreprise)

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """Vérifie la signature HMAC du webhook"""
    payload_str = json.dumps(payload, sort_keys=True)
    expected = hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

# Utilisation
@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.json
    
    if verify_webhook_signature(payload, signature, WEBHOOK_SECRET):
        # Traiter le webhook
        return {'status': 'ok'}, 200
    else:
        return {'error': 'Invalid signature'}, 401
```

---

## 🔁 Retry Policy

Si le webhook échoue (timeout, erreur 5xx, etc.) :

1. **Retry 1** : 5 minutes plus tard
2. **Retry 2** : 10 minutes plus tard
3. **Retry 3** : 20 minutes plus tard
4. **Retry 4** : 40 minutes plus tard
5. **Retry 5** : 80 minutes plus tard

Après 5 échecs, la task passe en FAILURE et est loggée.

---

## 📊 Monitoring

### Logs Celery (Terminal)
```
[2026-03-14 18:15:00] Task send_verification_webhook received
[2026-03-14 18:15:05] Task send_verification_webhook succeeded
```

### Logs Database
```sql
SELECT * FROM webhook_logs 
ORDER BY created_at DESC 
LIMIT 10;
```

### Vérifier via Python
```python
from app.db.session import AsyncSessionLocal
from app.models.logs import WebhookLog
from sqlalchemy import select
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(WebhookLog).order_by(WebhookLog.created_at.desc()).limit(5)
        )
        logs = result.scalars().all()
        for log in logs:
            print(f"{'✅' if log.success else '❌'} {log.event_type} - {log.response_status}")

asyncio.run(check())
```

---

## ✅ Conclusion

**Les webhooks sont FONCTIONNELS** mais nécessitent :
1. ⏳ Une `webhook_url` configurée pour l'entreprise
2. ⏳ Une URL accessible (webhook.site ou serveur réel)

**Pour tester maintenant** :
```bash
python test_webhook_with_url.py
```

Suivez les instructions pour configurer une URL webhook.site et tester l'envoi complet.
