# ☁️ Configuration Cloudinary - Guide Rapide

## 🎯 Étape 1 : Créer un Compte (2 minutes)

1. Aller sur : **https://cloudinary.com/users/register/free**
2. Remplir le formulaire :
   - Email
   - Mot de passe
   - Nom de votre cloud (ex: `kyc-platform-prod`)
3. Confirmer l'email reçu
4. Se connecter au dashboard

---

## 🔑 Étape 2 : Récupérer les Credentials (1 minute)

1. Dans le dashboard Cloudinary
2. Aller dans **Settings** (icône engrenage en haut à droite)
3. Cliquer sur **Access Keys** dans le menu gauche
4. Vous verrez :

```
Cloud Name: dxyz123abc
API Key: 123456789012345
API Secret: abcdefghijklmnopqrstuvwxyz-ABC
```

5. **Copier ces 3 valeurs**

---

## ⚙️ Étape 3 : Configurer dans .env (1 minute)

1. Ouvrir `e:/SAAS verification/backend/.env`
2. Modifier ces lignes :

```env
CLOUDINARY_CLOUD_NAME=dxyz123abc
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz-ABC
```

3. Sauvegarder le fichier

---

## 🔄 Étape 4 : Redémarrer Celery (1 minute)

1. Dans le terminal Celery, appuyer sur **Ctrl+C**
2. Relancer :
```bash
celery -A app.celery_app worker --loglevel=info --pool=solo
```

---

## 🧪 Étape 5 : Tester (2 minutes)

### Test Simple
```bash
cd "e:/SAAS verification/backend"
venv\Scripts\activate
python
```

Puis dans Python :
```python
import cloudinary
import cloudinary.uploader
from app.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# Créer une image test
from PIL import Image
img = Image.new('RGB', (100, 100), color='blue')
img.save('test_upload.jpg')

# Upload
result = cloudinary.uploader.upload('test_upload.jpg', folder='kyc/test')
print(f"✅ Upload réussi!")
print(f"URL: {result['secure_url']}")
```

Si vous voyez une URL comme `https://res.cloudinary.com/...`, c'est bon ! ✅

---

## 📊 Plan Gratuit Cloudinary

- **Stockage** : 25 GB
- **Bande passante** : 25 GB/mois
- **Transformations** : 25 000/mois
- **Vidéos** : 1 GB stockage, 1 GB bande passante

**Largement suffisant pour démarrer !**

---

## 🔍 Vérifier dans Dashboard

1. Aller dans **Media Library**
2. Vous devriez voir le dossier `kyc/`
3. Les images uploadées apparaîtront ici

---

## 🚀 Une fois configuré

Les images seront automatiquement :
1. ✅ Compressées (quality 85, format JPEG)
2. ✅ Redimensionnées (max 2048x2048)
3. ✅ Uploadées sur Cloudinary CDN
4. ✅ URLs sécurisées stockées dans DB
5. ✅ Accessibles mondialement via CDN

---

## ⏭️ Après Cloudinary

Configurer SMTP pour les emails → Voir `SMTP_SETUP.md`
