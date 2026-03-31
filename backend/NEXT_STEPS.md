# 🚀 Prochaines Étapes - Guide Pratique

## 📍 Vous êtes ici
✅ Backend FastAPI opérationnel  
✅ Celery tasks créées  
⏳ **Docker Desktop en cours de démarrage**

---

## 🎯 Étape 1: Redis (5 minutes)

### Une fois Docker Desktop démarré

#### 1.1 Lancer Redis
```bash
docker run -d -p 6379:6379 --name redis-kyc redis:7-alpine
```

#### 1.2 Vérifier que Redis tourne
```bash
docker ps
```

Vous devriez voir :
```
CONTAINER ID   IMAGE           STATUS          PORTS
abc123         redis:7-alpine  Up 10 seconds   0.0.0.0:6379->6379/tcp
```

#### 1.3 Tester la connexion Python
```bash
cd "e:/SAAS verification/backend"
venv\Scripts\activate
python -c "import redis; r = redis.Redis(); print('✅ Redis OK' if r.ping() else '❌ Erreur')"
```

---

## 🎯 Étape 2: Celery Worker (2 minutes)

### 2.1 Ouvrir un NOUVEAU terminal PowerShell

### 2.2 Lancer Celery
```bash
cd "e:/SAAS verification/backend"
venv\Scripts\activate
celery -A app.celery_app worker --loglevel=info --pool=solo
```

Vous devriez voir :
```
-------------- celery@DESKTOP v5.3.6
---- **** -----
--- * ***  * -- Windows-10
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         kyc_platform
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/1
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF

[tasks]
  . app.tasks.email_tasks.send_verification_initiated_email
  . app.tasks.image_tasks.compress_and_upload_image
  . app.tasks.webhook_tasks.send_verification_webhook
```

✅ **Laissez ce terminal ouvert** - c'est votre worker Celery

---

## 🎯 Étape 3: Tester les Tasks (5 minutes)

### 3.1 Dans un TROISIÈME terminal
```bash
cd "e:/SAAS verification/backend"
venv\Scripts\activate
python test_celery.py
```

### 3.2 Observer les logs
- **Terminal Celery** : Vous verrez les tasks s'exécuter en temps réel
- **Terminal test** : Vous verrez les résultats

---

## 🎯 Étape 4: Cloudinary (10 minutes)

### 4.1 Créer un compte gratuit
1. Aller sur https://cloudinary.com/users/register/free
2. S'inscrire (email + mot de passe)
3. Confirmer l'email

### 4.2 Récupérer les credentials
1. Dashboard Cloudinary → Settings → Access Keys
2. Copier :
   - Cloud Name
   - API Key
   - API Secret

### 4.3 Ajouter dans `.env`
Ouvrir `e:/SAAS verification/backend/.env` et modifier :
```env
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret
```

### 4.4 Redémarrer Celery
- Arrêter le worker (Ctrl+C)
- Relancer : `celery -A app.celery_app worker --loglevel=info --pool=solo`

---

## 🎯 Étape 5: SMTP Gmail (10 minutes)

### 5.1 Activer l'authentification à 2 facteurs
1. https://myaccount.google.com/security
2. Activer "Validation en deux étapes"

### 5.2 Créer un App Password
1. https://myaccount.google.com/apppasswords
2. Sélectionner "Autre (nom personnalisé)"
3. Entrer "KYC Platform"
4. Copier le mot de passe généré (16 caractères)

### 5.3 Ajouter dans `.env`
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM_EMAIL=noreply@votredomaine.com
```

### 5.4 Redémarrer Celery
- Arrêter le worker (Ctrl+C)
- Relancer : `celery -A app.celery_app worker --loglevel=info --pool=solo`

---

## 🎯 Étape 6: Test Workflow Complet (15 minutes)

### 6.1 Vérifier que tout tourne
- ✅ FastAPI : http://localhost:8000/health
- ✅ Redis : `docker ps`
- ✅ Celery : Terminal worker actif

### 6.2 Tester l'API complète
```bash
python test_api_simple.py
```

### 6.3 Observer le workflow
1. **Terminal API** : Requête reçue, réponse immédiate
2. **Terminal Celery** : Task email lancée en background
3. **Boîte email** : Email reçu (si SMTP configuré)

### 6.4 Tester upload de documents
```bash
# Créer un fichier test
python -c "from PIL import Image; img = Image.new('RGB', (100,100), 'red'); img.save('test.jpg')"

# Tester upload (via Swagger UI)
# http://localhost:8000/docs
# POST /api/v1/session/{token}/submit-documents
```

---

## 🎯 Étape 7: Vérifications Finales

### 7.1 Vérifier les logs DB
```python
# Dans un terminal Python
from app.db.session import AsyncSessionLocal
from app.models.logs import EmailLog, WebhookLog
from sqlalchemy import select
import asyncio

async def check_logs():
    async with AsyncSessionLocal() as db:
        # Emails
        result = await db.execute(select(EmailLog))
        emails = result.scalars().all()
        print(f"📧 Emails envoyés: {len(emails)}")
        
        # Webhooks
        result = await db.execute(select(WebhookLog))
        webhooks = result.scalars().all()
        print(f"🔗 Webhooks envoyés: {len(webhooks)}")

asyncio.run(check_logs())
```

### 7.2 Vérifier Cloudinary
1. Dashboard Cloudinary → Media Library
2. Vous devriez voir les images uploadées dans le dossier `kyc/`

### 7.3 Vérifier Redis
```bash
docker exec -it redis-kyc redis-cli
> KEYS *
> GET celery-task-meta-xxx
```

---

## ✅ Checklist Complète

### Infrastructure
- [ ] Docker Desktop démarré
- [ ] Redis conteneur lancé
- [ ] Connexion Redis testée
- [ ] Celery worker lancé
- [ ] FastAPI server lancé

### Configuration
- [ ] Cloudinary compte créé
- [ ] Cloudinary credentials dans `.env`
- [ ] Gmail App Password créé
- [ ] SMTP credentials dans `.env`

### Tests
- [ ] `test_celery.py` passé
- [ ] `test_api_simple.py` passé
- [ ] Email reçu dans boîte
- [ ] Image uploadée sur Cloudinary
- [ ] Logs DB vérifiés

---

## 🐛 Dépannage

### Redis ne démarre pas
```bash
# Vérifier si le port est utilisé
netstat -ano | findstr :6379

# Supprimer ancien conteneur
docker rm -f redis-kyc

# Relancer
docker run -d -p 6379:6379 --name redis-kyc redis:7-alpine
```

### Celery ne trouve pas Redis
```bash
# Vérifier l'URL dans .env
REDIS_URL=redis://localhost:6379/0

# Tester manuellement
python -c "import redis; redis.Redis().ping()"
```

### Email ne s'envoie pas
- Vérifier App Password (pas le mot de passe Gmail normal)
- Vérifier que 2FA est activé
- Regarder les logs Celery pour l'erreur exacte

### Cloudinary upload échoue
- Vérifier les credentials
- Vérifier la connexion internet
- Regarder les logs Celery

---

## 📞 Aide

Si vous êtes bloqué :
1. Consulter les logs Celery (terminal worker)
2. Consulter `e:/SAAS verification/backend/CELERY_TASKS.md`
3. Vérifier `.env` (credentials corrects)
4. Redémarrer Celery worker

---

**🎯 Une fois tout fonctionnel, vous aurez un système KYC complet avec traitement asynchrone !**
