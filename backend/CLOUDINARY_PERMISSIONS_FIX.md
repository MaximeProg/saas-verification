# 🔓 Débloquer les Permissions Cloudinary

## ❌ Erreur Actuelle
```
Request forbidden due to missing permissions (actions=["create"])
```

Votre compte Cloudinary (dcv43xjrd) est en mode **"prodenv"** avec restrictions activées.

---

## ✅ Solution : Désactiver les Restrictions

### Étape 1 : Accéder aux Paramètres de Sécurité

1. Aller sur : **https://cloudinary.com/console**
2. Se connecter avec vos identifiants
3. Cliquer sur l'icône **⚙️ Settings** (en haut à droite)
4. Dans le menu gauche, cliquer sur **🔒 Security**

---

### Étape 2 : Désactiver les Restrictions

#### A. Restricted Media Types
- Chercher la section **"Restricted media types"**
- **Décocher** toutes les cases :
  - [ ] Images
  - [ ] Videos
  - [ ] Raw files
- Cliquer **Save**

#### B. Upload Restrictions
- Chercher **"Upload restrictions"**
- S'assurer que **"Allow unsigned uploads"** est **activé** (ON)
- Ou au minimum, autoriser les **signed uploads**

#### C. Access Control
- Chercher **"Access control"**
- S'assurer que **"Strict transformations"** est **désactivé** (OFF)
- Autoriser les **transformations dynamiques**

---

### Étape 3 : Vérifier les Permissions API

1. Dans Settings → Security
2. Chercher **"API permissions"**
3. S'assurer que ces actions sont autorisées :
   - ✅ **create** (upload)
   - ✅ **read** (get resources)
   - ✅ **update** (modify)

---

### Étape 4 : Retester

```bash
cd "e:/SAAS verification/backend"
venv\Scripts\activate
python test_cloudinary_simple.py
```

Vous devriez voir :
```
✅ Upload réussi!
🔗 URL: https://res.cloudinary.com/dcv43xjrd/...
```

---

## 🔍 Vérification Alternative

Si les paramètres ne sont pas clairs, essayez ceci :

### Via Dashboard Cloudinary

1. Aller dans **Media Library**
2. Cliquer sur **Upload** (bouton en haut)
3. Essayer d'uploader une image manuellement
4. Si ça fonctionne → Les restrictions sont OK
5. Si ça échoue → Contacter support Cloudinary

---

## 🆘 Si Rien ne Fonctionne

### Option 1 : Créer un Nouveau Compte (5 min)

**Pourquoi ?**
- Votre compte actuel semble être un compte "production" avec restrictions
- Un nouveau compte gratuit n'aura pas ces restrictions

**Comment ?**
1. Utiliser un autre email
2. https://cloudinary.com/users/register/free
3. Copier les nouveaux credentials
4. Mettre à jour `.env`

### Option 2 : Contacter Support Cloudinary

- Email : support@cloudinary.com
- Expliquer : "Cannot upload images, getting 'missing permissions (actions=create)' error"
- Demander : Débloquer les permissions d'upload pour votre compte

---

## 📝 Checklist Actions

- [ ] Aller sur https://cloudinary.com/console
- [ ] Settings → Security
- [ ] Désactiver "Restricted media types"
- [ ] Activer "Allow unsigned uploads" OU "Signed uploads"
- [ ] Désactiver "Strict transformations"
- [ ] Sauvegarder
- [ ] Retester : `python test_cloudinary_simple.py`

---

**🎯 L'objectif est de faire fonctionner votre compte actuel (dcv43xjrd). Allez dans Settings → Security et désactivez les restrictions.**
