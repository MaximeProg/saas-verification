# 🔧 Guide de Configuration - Services Externes

## ✅ Déjà Configuré

- ✅ **Neon PostgreSQL** - Base de données connectée
- ✅ **Redis** - Broker Celery opérationnel (localhost:6379)
- ✅ **Celery Worker** - 6 tasks enregistrées et prêtes

---

## 📋 À Configurer

### 1. Cloudinary (Stockage Images) - 10 minutes

#### Pourquoi ?
- Upload et stockage sécurisé des documents
- Compression automatique optimisée
- CDN global pour accès rapide
- URLs sécurisées avec expiration

#### Étapes

**1.1 Créer un compte gratuit**
- Aller sur : https://cloudinary.com/users/register/free
- S'inscrire avec email
- Confirmer l'email

**1.2 Récupérer les credentials**
- Dashboard → Settings → Access Keys
- Copier :
  - **Cloud Name** (ex: `dxyz123abc`)
  - **API Key** (ex: `123456789012345`)
  - **API Secret** (ex: `abcdefghijklmnopqrstuvwxyz`)

**1.3 Ajouter dans `.env`**
Ouvrir `e:/SAAS verification/backend/.env` et modifier :
```env
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret
```

**1.4 Redémarrer Celery**
- Arrêter le worker (Ctrl+C dans le terminal Celery)
- Relancer : `celery -A app.celery_app worker --loglevel=info --pool=solo`

**1.5 Tester**
```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="votre_cloud_name",
    api_key="votre_api_key",
    api_secret="votre_api_secret"
)

# Test upload
result = cloudinary.uploader.upload("test.jpg")
print(result['secure_url'])
```

---

### 2. SMTP Gmail (Envoi Emails) - 10 minutes

#### Pourquoi ?
- Notifications email automatiques
- Email de vérification initié
- Email de résultat (approuvé/rejeté)

#### Étapes

**2.1 Activer l'authentification à 2 facteurs**
- Aller sur : https://myaccount.google.com/security
- Cliquer sur "Validation en deux étapes"
- Suivre les instructions pour activer

**2.2 Créer un App Password**
- Aller sur : https://myaccount.google.com/apppasswords
- Sélectionner "Autre (nom personnalisé)"
- Entrer "KYC Platform"
- Cliquer "Générer"
- **Copier le mot de passe** (16 caractères, format: `abcd efgh ijkl mnop`)

**2.3 Ajouter dans `.env`**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=noreply@kyc-platform.com
```

⚠️ **Important** : Utilisez le App Password, PAS votre mot de passe Gmail normal !

**2.4 Redémarrer Celery**
- Arrêter le worker (Ctrl+C)
- Relancer : `celery -A app.celery_app worker --loglevel=info --pool=solo`

**2.5 Tester**
```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test email")
msg['Subject'] = "Test KYC Platform"
msg['From'] = "votre_email@gmail.com"
msg['To'] = "votre_email@gmail.com"

with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login('votre_email@gmail.com', 'votre_app_password')
    server.send_message(msg)
    print("✅ Email envoyé!")
```

---

### 3. Alternative SMTP - Zoho Mail (Gratuit)

Si vous préférez Zoho :

**3.1 Créer compte**
- https://www.zoho.com/mail/zohomail-pricing.html (Plan gratuit)

**3.2 Configuration `.env`**
```env
SMTP_HOST=smtp.zoho.com
SMTP_PORT=587
SMTP_USER=votre_email@zoho.com
SMTP_PASSWORD=votre_mot_de_passe
SMTP_FROM_EMAIL=noreply@votredomaine.com
```

---

## 🧪 Tests Après Configuration

### Test 1 : Vérifier les variables
```bash
cd "e:/SAAS verification/backend"
venv\Scripts\activate
python -c "from app.config import settings; print('Cloudinary:', settings.CLOUDINARY_CLOUD_NAME); print('SMTP:', settings.SMTP_HOST)"
```

### Test 2 : Tester une task email
```python
from app.tasks.email_tasks import send_verification_initiated_email

task = send_verification_initiated_email.delay(
    recipient_email="votre_email@gmail.com",
    recipient_name="Test User",
    verification_id="KYC-TEST",
    verification_url="http://localhost:3000/session/test"
)

print(f"Task ID: {task.id}")
# Attendre 10s et vérifier votre boîte email
```

### Test 3 : Workflow API complet
```bash
python test_api_simple.py
```

Vérifier :
1. ✅ API répond instantanément
2. ✅ Task email lancée en background (logs Celery)
3. ✅ Email reçu dans boîte (si SMTP configuré)

---

## 📊 Vérification Logs

### Logs Celery (Terminal Worker)
Vous devriez voir :
```
[2026-03-14 18:15:00] Task app.tasks.email_tasks.send_verification_initiated_email[abc-123] received
[2026-03-14 18:15:01] Task app.tasks.email_tasks.send_verification_initiated_email[abc-123] succeeded
```

### Logs Database
```python
from app.db.session import AsyncSessionLocal
from app.models.logs import EmailLog
from sqlalchemy import select
import asyncio

async def check_logs():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(EmailLog).order_by(EmailLog.created_at.desc()).limit(5))
        logs = result.scalars().all()
        
        for log in logs:
            print(f"📧 {log.recipient_email} - {log.status} - {log.subject}")

asyncio.run(check_logs())
```

---

## ⚠️ Notes Importantes

### Cloudinary
- **Plan gratuit** : 25 GB stockage, 25 GB bande passante/mois
- Largement suffisant pour démarrer
- Upgrade possible si besoin

### Gmail SMTP
- **Limite** : 500 emails/jour (plan gratuit)
- Suffisant pour tests et petit volume
- Pour production : utiliser SendGrid, Mailgun, ou AWS SES

### Redis
- Déjà lancé via Docker (`emini-redis`)
- Pas besoin de configuration supplémentaire
- Accessible sur `localhost:6379`

---

## 🎯 Prochaine Action

**Maintenant** :
1. Configurer Cloudinary (10 min)
2. Configurer SMTP Gmail (10 min)
3. Redémarrer Celery worker
4. Tester workflow complet

**Ensuite** :
- Rate limiting avec Redis
- Détection doublons
- Frontend Next.js

---

## 🐛 Dépannage

### Task reste en PENDING
- Vérifier que Celery worker tourne
- Vérifier connexion Redis
- Regarder logs worker pour erreurs

### Email ne s'envoie pas
- Vérifier App Password (pas mot de passe normal)
- Vérifier 2FA activé sur Gmail
- Tester connexion SMTP manuellement

### Cloudinary upload échoue
- Vérifier credentials
- Vérifier connexion internet
- Regarder logs Celery pour erreur exacte

---

**✅ Redis et Celery sont opérationnels ! Il ne reste plus qu'à configurer Cloudinary et SMTP.**
