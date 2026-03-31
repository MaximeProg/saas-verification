# 📧 Configuration SMTP Gmail - Guide Rapide

## 🎯 Étape 1 : Activer 2FA sur Gmail (3 minutes)

1. Aller sur : **https://myaccount.google.com/security**
2. Chercher "Validation en deux étapes"
3. Cliquer sur "Commencer"
4. Suivre les instructions :
   - Entrer votre numéro de téléphone
   - Recevoir et entrer le code SMS
   - Activer la 2FA

---

## 🔑 Étape 2 : Créer un App Password (2 minutes)

1. Aller sur : **https://myaccount.google.com/apppasswords**
2. Vous devriez voir "Mots de passe des applications"
3. Sélectionner :
   - App : **Autre (nom personnalisé)**
   - Entrer : `KYC Platform`
4. Cliquer sur **Générer**
5. **Copier le mot de passe** affiché (16 caractères)

Exemple : `abcd efgh ijkl mnop`

⚠️ **Important** : Ce mot de passe ne sera affiché qu'une seule fois !

---

## ⚙️ Étape 3 : Configurer dans .env (1 minute)

1. Ouvrir `e:/SAAS verification/backend/.env`
2. Modifier ces lignes :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=noreply@kyc-platform.com
```

**Remplacer** :
- `votre_email@gmail.com` → Votre email Gmail
- `abcdefghijklmnop` → Le App Password (sans espaces)
- `noreply@kyc-platform.com` → Email affiché comme expéditeur

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

### Test Simple SMTP
```bash
cd "e:/SAAS verification/backend"
venv\Scripts\activate
python
```

Dans Python :
```python
import smtplib
from email.mime.text import MIMEText

# Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "votre_email@gmail.com"
SMTP_PASSWORD = "abcdefghijklmnop"

# Créer message
msg = MIMEText("Test email depuis KYC Platform")
msg['Subject'] = "Test SMTP"
msg['From'] = SMTP_USER
msg['To'] = SMTP_USER  # Envoi à vous-même

# Envoyer
try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        print("✅ Email envoyé avec succès!")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

Si vous recevez l'email, c'est bon ! ✅

### Test Task Celery
```python
from app.tasks.email_tasks import send_verification_initiated_email

task = send_verification_initiated_email.delay(
    recipient_email="votre_email@gmail.com",
    recipient_name="Test User",
    verification_id="KYC-TEST-001",
    verification_url="http://localhost:3000/session/test123"
)

print(f"✅ Task lancée: {task.id}")
print("📧 Vérifiez votre boîte email dans 10-20 secondes...")
```

---

## 📊 Limites Gmail

### Plan Gratuit
- **500 emails/jour** maximum
- Suffisant pour tests et petits volumes
- Pas de coût

### Pour Production (Recommandations)

**SendGrid** (Recommandé)
- 100 emails/jour gratuit
- 40 000 emails/mois à $19.95
- Excellent deliverability
- https://sendgrid.com/pricing/

**Mailgun**
- 5 000 emails/mois gratuit (3 mois)
- Puis $35/mois pour 50k emails
- https://www.mailgun.com/pricing/

**AWS SES**
- $0.10 pour 1000 emails
- Très économique à grande échelle
- https://aws.amazon.com/ses/pricing/

---

## 🎨 Templates Email Créés

### 1. Vérification Initiée
- ✅ Template HTML responsive
- ✅ Bouton CTA "Compléter ma vérification"
- ✅ Lien de vérification inclus
- ✅ Expiration 24h mentionnée

### 2. Vérification Complétée
- ✅ 2 versions (approuvé/rejeté)
- ✅ Couleurs différentes (vert/rouge)
- ✅ Raison du rejet si applicable

---

## 🐛 Dépannage

### Erreur "Username and Password not accepted"
- ❌ Vous utilisez votre mot de passe Gmail normal
- ✅ Utilisez le **App Password** (16 caractères)

### Erreur "2FA required"
- Activez la validation en deux étapes d'abord
- Puis créez un App Password

### Email ne s'envoie pas
1. Vérifier que 2FA est activé
2. Vérifier le App Password (pas d'espaces)
3. Tester avec le script simple ci-dessus
4. Regarder les logs Celery pour erreur exacte

### Email va dans spam
- Normal pour les tests
- En production, configurer SPF/DKIM/DMARC
- Utiliser un service professionnel (SendGrid)

---

## 📝 Vérification Logs

### Logs Celery
```
[2026-03-14 18:20:00] Task send_verification_initiated_email received
[2026-03-14 18:20:05] Task send_verification_initiated_email succeeded
```

### Logs Database
```python
from app.db.session import AsyncSessionLocal
from app.models.logs import EmailLog
from sqlalchemy import select
import asyncio

async def check_email_logs():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(EmailLog).order_by(EmailLog.created_at.desc()).limit(10)
        )
        logs = result.scalars().all()
        
        for log in logs:
            status_icon = "✅" if log.status == "sent" else "❌"
            print(f"{status_icon} {log.recipient_email} - {log.subject}")
            if log.error_message:
                print(f"   Erreur: {log.error_message}")

asyncio.run(check_email_logs())
```

---

## ✅ Une fois configuré

Tous les emails seront envoyés automatiquement :
1. ✅ Email au début de vérification (avec lien)
2. ✅ Email à la fin (approuvé/rejeté)
3. ✅ Retry automatique si échec
4. ✅ Logs dans DB pour audit

---

**⏭️ Après SMTP : Tester le workflow complet API → Celery → Email**
