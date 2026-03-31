# 🔧 Celery Tasks - Guide Complet

## 📋 Tasks Créées

### 1. Image Tasks (`app.tasks.image_tasks`)

#### `compress_and_upload_image`
Compresse et upload une image vers Cloudinary

**Paramètres**:
- `verification_id`: ID de la vérification
- `image_data_base64`: Image encodée en base64
- `image_type`: 'front', 'back', ou 'selfie'
- `filename`: Nom du fichier

**Workflow**:
1. Décode base64
2. Compresse l'image (JPEG, quality 85)
3. Redimensionne si > 2048x2048
4. Upload vers Cloudinary
5. Met à jour l'URL dans la DB

**Retry**: 3 tentatives avec backoff exponentiel

#### `process_verification_documents`
Traite tous les documents d'une vérification en parallèle

**Paramètres**:
- `verification_id`: ID de la vérification
- `front_data_base64`: Document recto (requis)
- `back_data_base64`: Document verso (optionnel)
- `selfie_data_base64`: Selfie (optionnel)

**Workflow**:
1. Lance des sous-tasks pour chaque image
2. Exécution en parallèle avec Celery groups

---

### 2. Email Tasks (`app.tasks.email_tasks`)

#### `send_verification_initiated_email`
Envoie un email de notification au début de la vérification

**Paramètres**:
- `recipient_email`: Email du destinataire
- `recipient_name`: Nom du destinataire
- `verification_id`: ID de la vérification
- `verification_url`: URL de vérification

**Template**: Email HTML avec bouton CTA

**Retry**: 3 tentatives, 1 minute entre chaque

#### `send_verification_completed_email`
Envoie un email de notification à la fin de la vérification

**Paramètres**:
- `recipient_email`: Email du destinataire
- `recipient_name`: Nom du destinataire
- `verification_id`: ID de la vérification
- `status`: 'approved' ou 'rejected'
- `rejection_reason`: Raison du rejet (optionnel)

**Templates**: 2 versions (approuvé/rejeté)

---

### 3. Webhook Tasks (`app.tasks.webhook_tasks`)

#### `send_verification_webhook`
Envoie un webhook HTTP POST à l'entreprise

**Paramètres**:
- `verification_id`: ID de la vérification
- `event_type`: Type d'événement
- `company_id`: ID de l'entreprise

**Workflow**:
1. Récupère l'entreprise et son webhook_url
2. Construit le payload JSON
3. Génère signature HMAC-SHA256
4. Envoie POST avec header X-Webhook-Signature
5. Log le résultat dans webhook_logs

**Retry**: 5 tentatives avec backoff exponentiel
- Retry 1: 5 minutes
- Retry 2: 10 minutes
- Retry 3: 20 minutes
- Retry 4: 40 minutes
- Retry 5: 80 minutes

**Events**:
- `verification.pending`
- `verification.in_review`
- `verification.approved`
- `verification.rejected`

---

## 🚀 Lancer Celery

### Windows
```bash
# Terminal 1: Redis (Docker)
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Terminal 2: Celery Worker
cd "e:/SAAS verification/backend"
venv\Scripts\activate
celery -A app.celery_app worker --loglevel=info --pool=solo
```

### Linux/Mac
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A app.celery_app worker --loglevel=info --concurrency=4
```

---

## 🧪 Tester les Tasks

### Test Manuel
```python
from app.tasks.email_tasks import send_verification_initiated_email

# Lancer une task
task = send_verification_initiated_email.delay(
    recipient_email="test@example.com",
    recipient_name="Jean Dupont",
    verification_id="KYC-001",
    verification_url="http://localhost:3000/session/abc123"
)

# Vérifier le statut
print(task.id)
print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE

# Attendre le résultat
result = task.get(timeout=10)
print(result)
```

### Script de Test
```bash
python test_celery.py
```

---

## 📊 Monitoring

### Flower (Web UI pour Celery)
```bash
pip install flower
celery -A app.celery_app flower
```

Accès: http://localhost:5555

### Logs
Les logs Celery apparaissent dans le terminal du worker.

### Database Logs
Tous les webhooks et emails sont loggés dans:
- `webhook_logs` table
- `email_logs` table

---

## ⚙️ Configuration

### Queues
- `images` - Traitement images
- `emails` - Envoi emails
- `webhooks` - Envoi webhooks
- `celery` - Queue par défaut

### Timeouts
- Task timeout: 30 minutes
- Soft timeout: 25 minutes
- HTTP timeout (webhooks): 30 secondes

### Retry Policy
- Max retries: 3-5 selon la task
- Backoff exponentiel
- Acks late activé (pour ne pas perdre de tasks)

---

## 🔐 Sécurité Webhooks

### Signature HMAC
Chaque webhook est signé avec HMAC-SHA256:

```python
import hmac
import hashlib
import json

def verify_webhook(payload, signature, secret):
    payload_str = json.dumps(payload, sort_keys=True)
    expected = hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### Côté Entreprise (Vérification)
```python
from flask import request

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.json
    
    if verify_webhook(payload, signature, WEBHOOK_SECRET):
        # Traiter le webhook
        return {'status': 'ok'}, 200
    else:
        return {'error': 'Invalid signature'}, 401
```

---

## 🐛 Dépannage

### Task ne démarre pas
1. Vérifier que Redis est lancé: `redis-cli ping`
2. Vérifier que Celery worker est lancé
3. Vérifier les logs du worker

### Task échoue
1. Consulter les logs Celery
2. Vérifier la configuration (.env)
3. Vérifier les logs DB (webhook_logs, email_logs)

### Retry infini
Les tasks ont un max_retries configuré (3-5).
Après épuisement, la task passe en FAILURE.

---

## 📝 Prochaines Améliorations

- [ ] Dead Letter Queue pour tasks échouées
- [ ] Monitoring avec Prometheus
- [ ] Rate limiting sur webhooks
- [ ] Batch processing pour emails
- [ ] Priorité des queues
