# 🚀 Déploiement sur Render - Guide Complet

## ✅ Ce qui est Déjà Prêt

Votre backend est **100% compatible Render** ! Voici pourquoi :

1. ✅ **PostgreSQL Neon** - Déjà hébergé en cloud
2. ✅ **Cloudinary** - Déjà hébergé en cloud
3. ✅ **SMTP Gmail** - Déjà configuré
4. ✅ **FastAPI** - Compatible ASGI
5. ✅ **Variables d'environnement** - Déjà dans `.env`

---

## 📋 Ce qu'il Faut Configurer sur Render

### 1. Redis (Obligatoire)

**Problème** : Vous utilisez Redis local (`localhost:6379`)  
**Solution** : Utiliser Redis hébergé

#### Option A : Redis sur Render (Recommandé)
```yaml
# Render créera automatiquement un Redis
Type: Redis
Plan: Free (25 MB)
```

#### Option B : Upstash Redis (Alternative gratuite)
```
URL: redis://default:password@region.upstash.io:6379
```

### 2. Celery Worker (Obligatoire)

**Problème** : Celery tourne localement  
**Solution** : Créer un service Render pour Celery

```yaml
Type: Background Worker
Build Command: pip install -r requirements.txt
Start Command: celery -A app.celery_app worker --loglevel=info
```

### 3. FastAPI Web Service

```yaml
Type: Web Service
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🔧 Fichiers à Créer

### 1. `requirements.txt` (Si pas déjà créé)

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
asyncpg==0.30.0
psycopg2-binary==2.9.11
alembic==1.14.0
pydantic==2.10.3
pydantic-settings==2.6.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20
redis==5.2.1
celery==5.6.2
pillow==11.0.0
cloudinary==1.41.0
requests==2.32.3
python-dotenv==1.0.1
```

### 2. `render.yaml` (Configuration Render)

```yaml
services:
  # FastAPI Web Service
  - type: web
    name: kyc-platform-api
    env: python
    region: frankfurt  # ou oregon, singapore
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        fromService:
          type: redis
          name: kyc-platform-redis
          property: connectionString
      - key: CELERY_BROKER_URL
        fromService:
          type: redis
          name: kyc-platform-redis
          property: connectionString
      - key: CELERY_RESULT_BACKEND
        fromService:
          type: redis
          name: kyc-platform-redis
          property: connectionString
      - key: CLOUDINARY_CLOUD_NAME
        sync: false
      - key: CLOUDINARY_API_KEY
        sync: false
      - key: CLOUDINARY_API_SECRET
        sync: false
      - key: SMTP_HOST
        value: smtp.gmail.com
      - key: SMTP_PORT
        value: 587
      - key: SMTP_USER
        sync: false
      - key: SMTP_PASSWORD
        sync: false
      - key: SMTP_FROM_EMAIL
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: JWT_ALGORITHM
        value: HS256
      - key: JWT_EXPIRATION_MINUTES
        value: 1440

  # Celery Worker
  - type: worker
    name: kyc-platform-worker
    env: python
    region: frankfurt
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A app.celery_app worker --loglevel=info --pool=solo
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: REDIS_URL
        fromService:
          type: redis
          name: kyc-platform-redis
          property: connectionString
      - key: CELERY_BROKER_URL
        fromService:
          type: redis
          name: kyc-platform-redis
          property: connectionString
      - key: CELERY_RESULT_BACKEND
        fromService:
          type: redis
          name: kyc-platform-redis
          property: connectionString
      - key: CLOUDINARY_CLOUD_NAME
        sync: false
      - key: CLOUDINARY_API_KEY
        sync: false
      - key: CLOUDINARY_API_SECRET
        sync: false
      - key: SMTP_HOST
        value: smtp.gmail.com
      - key: SMTP_PORT
        value: 587
      - key: SMTP_USER
        sync: false
      - key: SMTP_PASSWORD
        sync: false
      - key: SMTP_FROM_EMAIL
        sync: false

  # Redis
  - type: redis
    name: kyc-platform-redis
    region: frankfurt
    plan: free
    maxmemoryPolicy: allkeys-lru
```

### 3. `Procfile` (Alternative simple)

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: celery -A app.celery_app worker --loglevel=info --pool=solo
```

---

## 🔐 Variables d'Environnement à Configurer

Sur Render Dashboard, ajouter ces variables :

### Obligatoires
```
DATABASE_URL=postgresql+asyncpg://user:pass@neon.tech/db
REDIS_URL=redis://...  (auto si Redis Render)
CLOUDINARY_CLOUD_NAME=deqfth8zn
CLOUDINARY_API_KEY=285959...
CLOUDINARY_API_SECRET=...
SMTP_USER=kakpokouassimaxime80@gmail.com
SMTP_PASSWORD=...
SMTP_FROM_EMAIL=kakpokouassimaxime80@gmail.com
JWT_SECRET_KEY=...
```

### Optionnelles (avec valeurs par défaut)
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
```

---

## 📝 Modifications du Code Nécessaires

### 1. Modifier `app/config.py`

Ajouter support pour `PORT` dynamique :

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    PORT: int = 8000  # Render injecte $PORT
    
    # Redis URL - utiliser variable d'environnement
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = Field(default="")
    CELERY_RESULT_BACKEND: str = Field(default="")
    
    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL.replace("/0", "/1")
```

### 2. Modifier `app/celery_app.py`

```python
from app.config import settings

celery_app = Celery(
    "kyc_platform",
    broker=settings.celery_broker,  # Au lieu de settings.CELERY_BROKER_URL
    backend=settings.celery_backend  # Au lieu de settings.CELERY_RESULT_BACKEND
)
```

### 3. Modifier `app/main.py`

Ajouter CORS pour production :

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)

# CORS pour production
origins = [
    "http://localhost:3000",  # Frontend local
    "https://votre-frontend.vercel.app",  # Frontend prod
    "https://kyc-platform-api.onrender.com",  # API Render
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 Processus de Déploiement

### Étape 1 : Préparer le Repo Git

```bash
# Créer .gitignore si pas déjà fait
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "venv/" >> .gitignore

# Commit et push
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Étape 2 : Créer les Services sur Render

1. **Aller sur** : https://dashboard.render.com
2. **Créer Redis** :
   - New → Redis
   - Name: `kyc-platform-redis`
   - Plan: Free
   - Create

3. **Créer Web Service** :
   - New → Web Service
   - Connect GitHub repo
   - Name: `kyc-platform-api`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free
   - Add environment variables
   - Create

4. **Créer Worker** :
   - New → Background Worker
   - Connect same repo
   - Name: `kyc-platform-worker`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `celery -A app.celery_app worker --loglevel=info --pool=solo`
   - Add environment variables
   - Create

### Étape 3 : Configurer les Variables

Pour chaque service (API + Worker), ajouter :
- DATABASE_URL
- REDIS_URL (copier depuis Redis service)
- CLOUDINARY_*
- SMTP_*
- JWT_SECRET_KEY

### Étape 4 : Déployer

Render déploie automatiquement à chaque push Git !

---

## 🔍 Vérifications Post-Déploiement

### 1. Vérifier l'API
```bash
curl https://kyc-platform-api.onrender.com/health
# Devrait retourner: {"status": "healthy"}
```

### 2. Vérifier la Documentation
```
https://kyc-platform-api.onrender.com/docs
```

### 3. Vérifier Celery Worker
Dans Render Dashboard → Worker → Logs :
```
[tasks]
  . app.tasks.email_tasks.send_verification_completed_email
  . app.tasks.image_tasks.compress_and_upload_image
  ...
celery@worker ready.
```

### 4. Tester une Vérification Complète
```bash
curl -X POST https://kyc-platform-api.onrender.com/api/v1/verifications \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## ⚠️ Limitations Plan Gratuit Render

### Web Service (API)
- ✅ 750 heures/mois
- ⚠️ Sleep après 15 min d'inactivité
- ⚠️ Réveil : ~30 secondes
- ✅ 512 MB RAM
- ✅ SSL gratuit

### Background Worker (Celery)
- ✅ 750 heures/mois
- ⚠️ Pas de sleep (toujours actif)
- ✅ 512 MB RAM

### Redis
- ✅ 25 MB storage
- ✅ Pas de sleep
- ⚠️ Données volatiles (pas de persistence)

**Solution pour Sleep** :
- Utiliser un cron job pour ping l'API toutes les 10 min
- Ou passer au plan payant ($7/mois)

---

## 💰 Coûts Estimés

### Plan Gratuit (Recommandé pour MVP)
```
API Web Service:     $0/mois (avec sleep)
Celery Worker:       $0/mois
Redis:               $0/mois
PostgreSQL Neon:     $0/mois
Cloudinary:          $0/mois
SMTP Gmail:          $0/mois
---
TOTAL:               $0/mois ✅
```

### Plan Payant (Production)
```
API Web Service:     $7/mois (pas de sleep)
Celery Worker:       $7/mois
Redis:               $10/mois (1 GB)
PostgreSQL Neon:     $19/mois (Pro)
Cloudinary:          $0/mois (Free OK)
SMTP Gmail:          $0/mois
---
TOTAL:               $43/mois
```

---

## 🎯 Checklist Déploiement

- [ ] Créer `requirements.txt`
- [ ] Créer `render.yaml` ou `Procfile`
- [ ] Modifier `app/config.py` pour Redis dynamique
- [ ] Ajouter CORS pour production
- [ ] Push code sur GitHub
- [ ] Créer Redis sur Render
- [ ] Créer Web Service sur Render
- [ ] Créer Worker sur Render
- [ ] Configurer variables d'environnement
- [ ] Tester `/health` endpoint
- [ ] Tester `/docs` documentation
- [ ] Vérifier logs Celery
- [ ] Tester création vérification
- [ ] Vérifier email reçu
- [ ] Vérifier image sur Cloudinary

---

## 📚 Ressources

- **Render Docs** : https://render.com/docs
- **Render Python** : https://render.com/docs/deploy-fastapi
- **Render Redis** : https://render.com/docs/redis
- **Render Workers** : https://render.com/docs/background-workers

---

## ✅ Résumé

**Configurations nécessaires** :
1. ✅ Créer `requirements.txt`
2. ✅ Créer `render.yaml` (optionnel mais recommandé)
3. ✅ Modifier `config.py` pour Redis dynamique
4. ✅ Configurer 3 services Render (API, Worker, Redis)
5. ✅ Ajouter variables d'environnement

**Temps estimé** : 30-45 minutes

**Votre backend est déjà 95% prêt pour Render !** Il suffit de créer les fichiers de configuration et les services. 🚀
