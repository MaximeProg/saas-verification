# KYC Platform - Backend API

Backend FastAPI pour la plateforme SaaS de vérification d'identité (KYC).

## 🚀 Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv
```

### 2. Activer l'environnement virtuel

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

Copier `.env.example` vers `.env` et configurer les variables d'environnement.

Le fichier `.env` est déjà configuré avec la connexion Neon PostgreSQL.

## 🗄️ Base de données

### Créer les tables

Les tables sont créées automatiquement au démarrage de l'application.

Ou utiliser Alembic pour les migrations:

```bash
# Créer une migration initiale
alembic revision --autogenerate -m "Initial migration"

# Appliquer les migrations
alembic upgrade head
```

## 🏃 Lancer l'application

### Mode développement

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Mode production

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 Documentation API

Une fois l'application lancée:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Tests

```bash
pytest
```

## 📁 Structure du projet

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration
│   ├── db/                  # Database
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/              # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── verification.py
│   │   ├── admin.py
│   │   ├── logs.py
│   │   ├── blacklist.py
│   │   └── duplicate.py
│   ├── schemas/             # Schémas Pydantic (à créer)
│   ├── api/                 # Endpoints API (à créer)
│   ├── services/            # Logique métier (à créer)
│   ├── core/                # Sécurité, utils (à créer)
│   └── tasks/               # Celery tasks (à créer)
├── alembic/                 # Migrations
├── requirements.txt
├── .env
└── README.md
```

## 🔑 Variables d'environnement

Voir `.env.example` pour la liste complète des variables.

## 📝 Prochaines étapes

1. ✅ Configuration base de données Neon
2. ✅ Modèles SQLAlchemy
3. ⏳ Schémas Pydantic
4. ⏳ Endpoints API
5. ⏳ Authentification JWT
6. ⏳ Celery tasks
7. ⏳ Tests
