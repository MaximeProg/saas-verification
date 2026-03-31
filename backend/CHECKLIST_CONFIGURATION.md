# ✅ Checklist Configuration - À Suivre

## 📋 Étape par Étape

### 1️⃣ Cloudinary (10 minutes)

#### Actions
- [ ] Ouvrir https://cloudinary.com/users/register/free
- [ ] Créer un compte (email + mot de passe)
- [ ] Confirmer l'email reçu
- [ ] Se connecter au dashboard
- [ ] Aller dans Settings → Access Keys
- [ ] Copier les 3 valeurs :
  ```
  Cloud Name: _________________
  API Key: _________________
  API Secret: _________________
  ```

#### Configuration
- [ ] Ouvrir `e:/SAAS verification/backend/.env`
- [ ] Modifier les lignes :
  ```env
  CLOUDINARY_CLOUD_NAME=votre_cloud_name
  CLOUDINARY_API_KEY=votre_api_key
  CLOUDINARY_API_SECRET=votre_api_secret
  ```
- [ ] Sauvegarder le fichier

#### Test
- [ ] Exécuter : `python test_cloudinary.py`
- [ ] Vérifier que tous les tests passent ✅
- [ ] Vérifier dans Media Library Cloudinary

---

### 2️⃣ SMTP Gmail (10 minutes)

#### Actions
- [ ] Ouvrir https://myaccount.google.com/security
- [ ] Activer "Validation en deux étapes"
- [ ] Suivre les instructions (SMS)
- [ ] Ouvrir https://myaccount.google.com/apppasswords
- [ ] Sélectionner "Autre (nom personnalisé)"
- [ ] Entrer "KYC Platform"
- [ ] Cliquer "Générer"
- [ ] Copier le mot de passe (16 caractères)
  ```
  App Password: ____ ____ ____ ____
  ```

#### Configuration
- [ ] Ouvrir `e:/SAAS verification/backend/.env`
- [ ] Modifier les lignes :
  ```env
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=votre_email@gmail.com
  SMTP_PASSWORD=abcdefghijklmnop
  SMTP_FROM_EMAIL=noreply@kyc-platform.com
  ```
- [ ] **Retirer les espaces** du App Password
- [ ] Sauvegarder le fichier

#### Test
- [ ] Exécuter : `python test_smtp.py`
- [ ] Vérifier que tous les tests passent ✅
- [ ] Vérifier email reçu dans boîte Gmail

---

### 3️⃣ Redémarrer Celery (1 minute)

- [ ] Dans le terminal Celery, appuyer sur **Ctrl+C**
- [ ] Relancer :
  ```bash
  celery -A app.celery_app worker --loglevel=info --pool=solo
  ```
- [ ] Vérifier que le worker démarre sans erreur

---

### 4️⃣ Test Workflow Complet (5 minutes)

#### Test API avec Tasks Background
- [ ] Exécuter : `python test_api_simple.py`
- [ ] Vérifier réponse API instantanée
- [ ] Observer logs Celery (task email lancée)
- [ ] Vérifier email reçu dans boîte

#### Test Upload Documents
- [ ] Créer image test :
  ```python
  from PIL import Image
  img = Image.new('RGB', (500, 500), 'green')
  img.save('test_doc.jpg')
  ```
- [ ] Aller sur http://localhost:8000/docs
- [ ] Tester `POST /api/v1/session/{token}/submit-documents`
- [ ] Observer logs Celery (compression + upload)
- [ ] Vérifier image dans Cloudinary Media Library

---

## 🎯 Résultat Attendu

Une fois tout configuré, le workflow complet fonctionnera :

```
1. Entreprise → POST /verifications/initiate
   ↓ (< 100ms)
2. API → Réponse immédiate avec verification_url
   ↓ (background)
3. Celery → Envoi email avec lien
   ↓
4. Utilisateur → Ouvre lien, upload documents
   ↓ (< 200ms)
5. API → Réponse immédiate "Documents reçus"
   ↓ (background)
6. Celery → Compression images
   ↓
7. Celery → Upload vers Cloudinary
   ↓
8. Celery → Update URLs dans DB
   ↓
9. Admin → Review et approve/reject
   ↓ (background)
10. Celery → Webhook vers entreprise
    ↓
11. Celery → Email notification utilisateur
    ↓
12. ✅ Workflow terminé
```

---

## 📊 Vérifications Finales

### Vérifier Logs Database
```bash
python -c "
from app.db.session import AsyncSessionLocal
from app.models.logs import EmailLog, WebhookLog
from sqlalchemy import select
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        emails = await db.execute(select(EmailLog))
        webhooks = await db.execute(select(WebhookLog))
        print(f'📧 Emails: {len(emails.scalars().all())}')
        print(f'🔗 Webhooks: {len(webhooks.scalars().all())}')

asyncio.run(check())
"
```

### Vérifier Cloudinary Media Library
- Aller sur : https://cloudinary.com/console/media_library
- Dossier `kyc/` devrait contenir les images uploadées

### Vérifier Emails Reçus
- Boîte Gmail
- Chercher "KYC Platform" ou "Vérification"

---

## 🐛 Problèmes Courants

### Cloudinary : "Invalid credentials"
- ✅ Vérifier que les 3 valeurs sont correctes
- ✅ Pas d'espaces avant/après
- ✅ Copier depuis Dashboard → Settings → Access Keys

### SMTP : "Username and Password not accepted"
- ✅ Utiliser App Password (16 caractères)
- ✅ PAS le mot de passe Gmail normal
- ✅ Retirer les espaces du App Password
- ✅ Vérifier que 2FA est activé

### Task Celery échoue
- ✅ Redémarrer Celery après modification .env
- ✅ Vérifier logs Celery pour erreur exacte
- ✅ Vérifier connexion internet

---

## ⏭️ Après Configuration

Une fois Cloudinary et SMTP configurés :
1. ✅ Tester workflow complet
2. ✅ Implémenter rate limiting
3. ✅ Activer détection doublons
4. ✅ Démarrer frontend Next.js

---

**🎯 Temps estimé total : 20-25 minutes pour tout configurer**
