# 🚀 Guide de Démarrage Rapide - Backend KYC

## ✅ Étapes Complétées

- [x] Structure du projet créée
- [x] Connexion Neon PostgreSQL configurée
- [x] 8 tables créées dans la base de données
- [x] Modèles SQLAlchemy avec relations
- [x] Schémas Pydantic pour validation
- [x] Endpoints API implémentés
- [x] Authentification JWT et API Keys

## 📦 Installation (Déjà fait)

```bash
# Environnement virtuel créé et activé
python -m venv venv
venv\Scripts\activate

# Dépendances installées
pip install -r requirements.txt
```

## 🗄️ Base de Données

**Base de données**: Neon PostgreSQL (déjà configurée)

**Tables créées**:
- ✅ companies
- ✅ verifications  
- ✅ admin_users
- ✅ api_logs
- ✅ webhook_logs
- ✅ email_logs
- ✅ blacklist
- ✅ verification_duplicates

## 🏃 Lancer le Serveur

### Option 1: Script batch (Windows)
```bash
start_server.bat
```

### Option 2: Commande directe
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur: **http://localhost:8000**

## 📚 Documentation API

Une fois le serveur lancé:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔑 Créer un Administrateur

Première connexion - créer le premier admin:

```bash
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.admin import AdminUser
from app.core.security import get_password_hash

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = AdminUser(
            username='admin',
            email='admin@kyc.com',
            password_hash=get_password_hash('admin123'),
            role='super_admin'
        )
        db.add(admin)
        await db.commit()
        print('✅ Admin créé: admin / admin123')

asyncio.run(create_admin())
"
```

## 🧪 Tester l'API

### 1. Créer une entreprise de test

```bash
python -c "
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.company import Company
from app.core.security import generate_api_keys, generate_webhook_secret

async def create_company():
    async with AsyncSessionLocal() as db:
        public_key, secret_key = generate_api_keys()
        company = Company(
            company_name='Test Company',
            email='test@company.com',
            phone='+33612345678',
            country='France',
            address='123 Test St',
            rccm='RC123',
            tax_number='FR123',
            legal_representative='John Doe',
            status='production',
            is_validated=True,
            subscription_plan='business',
            monthly_quota=1000,
            public_key=public_key,
            secret_key=secret_key,
            webhook_secret=generate_webhook_secret()
        )
        db.add(company)
        await db.commit()
        print(f'✅ Entreprise créée')
        print(f'🔑 Secret Key: {secret_key}')

asyncio.run(create_company())
"
```

### 2. Tester avec curl

```bash
# Initier une vérification
curl -X POST http://localhost:8000/api/v1/verifications/initiate \
  -H "Authorization: Bearer VOTRE_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jean Dupont",
    "email": "jean@example.com",
    "external_reference": "REF-001"
  }'
```

### 3. Tester avec le script Python

```bash
python test_api.py
```

## 📊 Endpoints Disponibles

### Verifications (`/api/v1/verifications`)
- `POST /initiate` - Initier une vérification
- `GET /{verification_id}` - Récupérer une vérification
- `GET /` - Lister les vérifications (paginé)
- `POST /{verification_id}/review` - Valider/Rejeter (admin)

### Companies (`/api/v1/companies`)
- `POST /register` - Inscription entreprise
- `POST /login` - Login entreprise
- `GET /me` - Info entreprise connectée
- `GET /api-keys` - Récupérer clés API
- `POST /api-keys/regenerate` - Régénérer clés

### Admin (`/api/v1/admin`)
- `POST /register` - Créer admin (premier uniquement)
- `POST /login` - Login admin
- `GET /me` - Info admin connecté
- `GET /companies` - Lister entreprises
- `POST /companies/{id}/validate` - Valider entreprise
- `GET /verifications` - Lister toutes vérifications

## 🔐 Authentification

### Pour les entreprises (API)
```
Authorization: Bearer sk_votre_secret_key
```

### Pour les admins (Dashboard)
```
Authorization: Bearer jwt_token
```

## 📝 Prochaines Étapes

1. ⏳ Implémenter upload de fichiers
2. ⏳ Configurer Celery pour tâches background
3. ⏳ Intégrer Cloudinary pour stockage
4. ⏳ Configurer SMTP pour emails
5. ⏳ Implémenter webhooks
6. ⏳ Ajouter rate limiting
7. ⏳ Tests unitaires

## 🐛 Dépannage

### Erreur de connexion DB
Vérifier que l'URL Neon est correcte dans `.env`

### Port déjà utilisé
Changer le port: `--port 8001`

### Import errors
Réinstaller: `pip install -r requirements.txt`
