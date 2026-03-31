# 🔧 Installation Redis + Celery - Windows

## 📦 Option 1: Redis avec WSL (Recommandé)

### 1. Installer WSL
```powershell
wsl --install
```

### 2. Installer Redis dans WSL
```bash
sudo apt update
sudo apt install redis-server
```

### 3. Démarrer Redis
```bash
sudo service redis-server start
```

### 4. Vérifier
```bash
redis-cli ping
# Devrait retourner: PONG
```

---

## 📦 Option 2: Redis avec Docker (Plus simple)

### 1. Installer Docker Desktop
Télécharger: https://www.docker.com/products/docker-desktop/

### 2. Lancer Redis
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### 3. Vérifier
```bash
docker ps
```

---

## 📦 Option 3: Memurai (Redis pour Windows natif)

### 1. Télécharger Memurai
https://www.memurai.com/get-memurai

### 2. Installer et démarrer le service

### 3. Redis sera accessible sur localhost:6379

---

## 🧪 Tester la connexion Redis

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # True
r.set('test', 'hello')
r.get('test')  # b'hello'
```

---

## ⚙️ Configuration Celery

Celery est déjà installé dans requirements.txt.

### Démarrer Celery Worker
```bash
celery -A app.celery_app worker --loglevel=info --pool=solo
```

Note: `--pool=solo` est nécessaire sur Windows

---

## 🎯 Prochaines étapes

1. ✅ Installer Redis (choisir une option ci-dessus)
2. ⏳ Créer celery_app.py
3. ⏳ Créer tasks (compression, upload, emails, webhooks)
4. ⏳ Tester avec un worker
