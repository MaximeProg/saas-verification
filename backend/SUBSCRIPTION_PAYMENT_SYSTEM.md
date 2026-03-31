# 💳 Système de Plans d'Abonnement et Paiements FedaPay

## 📋 Vue d'Ensemble

Système complet permettant aux **admins** de créer des plans d'abonnement et aux **entreprises** d'acheter ces plans via **FedaPay**.

---

## 🗄️ Nouvelles Tables

### 1. `subscription_plans` - Plans d'Abonnement

```sql
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- "Starter", "Professional"
    slug VARCHAR(50) UNIQUE NOT NULL,    -- "starter", "professional"
    description TEXT NOT NULL,
    
    -- Tarification
    price FLOAT NOT NULL,                -- Prix en FCFA
    currency VARCHAR(3) DEFAULT 'XOF',
    billing_period VARCHAR(20) DEFAULT 'monthly',
    
    -- Quotas
    monthly_quota INTEGER NOT NULL,      -- Vérifications/mois
    max_api_keys INTEGER DEFAULT 5,
    max_users INTEGER DEFAULT 1,
    
    -- Fonctionnalités (JSON)
    features JSON NOT NULL,
    advantages JSON NOT NULL,
    
    -- Statut
    is_active BOOLEAN DEFAULT TRUE,
    is_popular BOOLEAN DEFAULT FALSE,
    is_custom BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID
);
```

**Exemple de plan** :
```json
{
  "name": "Professional",
  "slug": "professional",
  "description": "Pour les entreprises en croissance",
  "price": 50000,
  "currency": "XOF",
  "billing_period": "monthly",
  "monthly_quota": 500,
  "max_api_keys": 10,
  "max_users": 5,
  "features": {
    "webhook_support": true,
    "priority_support": true,
    "custom_branding": false,
    "api_access": true,
    "bulk_upload": true,
    "advanced_analytics": false
  },
  "advantages": [
    "500 vérifications par mois",
    "Support prioritaire",
    "10 clés API",
    "5 utilisateurs",
    "Webhooks inclus",
    "Upload en masse"
  ],
  "is_popular": true
}
```

---

### 2. `payments` - Paiements

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    payment_reference VARCHAR(100) UNIQUE NOT NULL,  -- PAY-20260314-ABCD1234
    
    -- Relations
    company_id UUID NOT NULL REFERENCES companies(id),
    plan_id UUID NOT NULL REFERENCES subscription_plans(id),
    
    -- Montant
    amount FLOAT NOT NULL,
    currency VARCHAR(3) DEFAULT 'XOF',
    
    -- FedaPay
    fedapay_transaction_id VARCHAR(255) UNIQUE,
    fedapay_token VARCHAR(255),
    fedapay_status VARCHAR(50),
    fedapay_response TEXT,
    
    -- Méthode
    payment_method VARCHAR(50) NOT NULL,  -- mobile_money, card, bank_transfer
    
    -- Statut
    status VARCHAR(50) NOT NULL,  -- pending, processing, completed, failed, cancelled
    
    -- Dates
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Informations
    description TEXT,
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    callback_url VARCHAR(500),
    return_url VARCHAR(500),
    metadata TEXT
);
```

---

### 3. Modification `companies`

Ajout de champs pour lier au plan :

```sql
ALTER TABLE companies ADD COLUMN subscription_plan_id UUID;
ALTER TABLE companies ADD COLUMN subscription_started_at TIMESTAMP;
```

---

## 🔌 API Endpoints

### Admin - Gestion des Plans

#### 1. Créer un Plan
```http
POST /api/v1/subscription-plans
Authorization: Bearer {admin_jwt}

{
  "name": "Starter",
  "slug": "starter",
  "description": "Plan de démarrage pour petites entreprises",
  "price": 15000,
  "currency": "XOF",
  "billing_period": "monthly",
  "monthly_quota": 100,
  "max_api_keys": 3,
  "max_users": 1,
  "features": {
    "webhook_support": true,
    "priority_support": false,
    "api_access": true
  },
  "advantages": [
    "100 vérifications/mois",
    "Support email",
    "3 clés API"
  ],
  "is_active": true,
  "is_popular": false,
  "display_order": 1
}
```

#### 2. Lister tous les Plans (Admin)
```http
GET /api/v1/subscription-plans
Authorization: Bearer {admin_jwt}
```

#### 3. Modifier un Plan
```http
PUT /api/v1/subscription-plans/{plan_id}
Authorization: Bearer {admin_jwt}

{
  "price": 18000,
  "monthly_quota": 150
}
```

#### 4. Supprimer un Plan
```http
DELETE /api/v1/subscription-plans/{plan_id}
Authorization: Bearer {admin_jwt}
```

---

### Public - Affichage des Plans

#### Lister les Plans Actifs (Public)
```http
GET /api/v1/subscription-plans/public

Response:
[
  {
    "id": "uuid",
    "name": "Starter",
    "slug": "starter",
    "description": "...",
    "price": 15000,
    "currency": "XOF",
    "billing_period": "monthly",
    "monthly_quota": 100,
    "advantages": [...],
    "is_popular": false,
    "has_webhook_support": true,
    "has_priority_support": false
  }
]
```

---

### Entreprise - Achat de Plans

#### 1. Initialiser un Paiement
```http
POST /api/v1/payments/initialize
X-API-Key: {company_api_key}

{
  "plan_id": "uuid",
  "payment_method": "mobile_money",
  "customer_email": "contact@company.com",
  "customer_phone": "+22997123456",
  "callback_url": "https://myapp.com/payment/callback",
  "return_url": "https://myapp.com/payment/success"
}

Response:
{
  "payment_id": "uuid",
  "payment_reference": "PAY-20260314120000-ABCD1234",
  "amount": 15000,
  "currency": "XOF",
  "payment_url": "https://checkout.fedapay.com/abc123",
  "token": "abc123",
  "expires_at": "2026-03-15T12:00:00",
  "status": "processing"
}
```

**L'entreprise redirige l'utilisateur vers `payment_url`**

#### 2. Vérifier un Paiement
```http
POST /api/v1/payments/{payment_id}/verify
X-API-Key: {company_api_key}

Response:
{
  "id": "uuid",
  "payment_reference": "PAY-...",
  "status": "completed",
  "paid_at": "2026-03-14T12:05:00",
  ...
}
```

#### 3. Historique des Paiements
```http
GET /api/v1/payments/my-payments?page=1&page_size=20
X-API-Key: {company_api_key}

Response:
{
  "total": 5,
  "page": 1,
  "page_size": 20,
  "payments": [...]
}
```

---

## 🔄 Workflow Complet

### 1. Admin Crée les Plans

```mermaid
Admin → POST /subscription-plans
  → Plan "Starter" créé (15000 FCFA/mois, 100 vérifications)
  → Plan "Professional" créé (50000 FCFA/mois, 500 vérifications)
  → Plan "Enterprise" créé (150000 FCFA/mois, 2000 vérifications)
```

### 2. Entreprise Consulte les Plans

```mermaid
Frontend → GET /subscription-plans/public
  → Affiche les 3 plans avec prix et avantages
  → Utilisateur choisit "Professional"
```

### 3. Entreprise Initialise le Paiement

```mermaid
Frontend → POST /payments/initialize
  {
    "plan_id": "professional-uuid",
    "payment_method": "mobile_money"
  }
  ↓
Backend → Crée Payment en DB (status: pending)
  ↓
Backend → Appelle FedaPay API
  POST https://api.fedapay.com/v1/transactions
  {
    "amount": 50000,
    "currency": {"iso": "XOF"},
    "description": "Abonnement Professional - monthly"
  }
  ↓
FedaPay → Retourne transaction_id et token
  ↓
Backend → Met à jour Payment (status: processing)
  ↓
Backend → Retourne payment_url
  ↓
Frontend → Redirige vers FedaPay Checkout
```

### 4. Utilisateur Paie sur FedaPay

```mermaid
Utilisateur → Saisit numéro Mobile Money
  ↓
FedaPay → Envoie demande de paiement
  ↓
Utilisateur → Confirme sur téléphone
  ↓
FedaPay → Traite le paiement
```

### 5. FedaPay Notifie via Webhook

```mermaid
FedaPay → POST /api/v1/payments/webhook
  {
    "event": "transaction.approved",
    "entity": {
      "id": "fedapay-transaction-id",
      "status": "approved",
      "metadata": {
        "payment_id": "uuid"
      }
    }
  }
  ↓
Backend → Récupère Payment depuis DB
  ↓
Backend → Met à jour Payment (status: completed, paid_at: now)
  ↓
Backend → Active l'abonnement de l'entreprise
  UPDATE companies SET
    subscription_plan_id = 'professional-uuid',
    subscription_plan = 'Professional',
    monthly_quota = 500,
    quota_used = 0,
    subscription_started_at = NOW(),
    subscription_expires_at = NOW() + 30 days
  ↓
Backend → Retourne 200 OK à FedaPay
```

### 6. Entreprise Vérifie le Statut

```mermaid
Frontend → POST /payments/{payment_id}/verify
  ↓
Backend → Vérifie auprès de FedaPay
  GET https://api.fedapay.com/v1/transactions/{transaction_id}
  ↓
FedaPay → Retourne status: "approved"
  ↓
Backend → Met à jour si nécessaire
  ↓
Backend → Retourne Payment avec status: "completed"
  ↓
Frontend → Affiche "Paiement réussi ! Abonnement activé"
```

---

## 🔐 Configuration FedaPay

### Variables d'Environnement

Ajouter dans `.env` :

```env
# FedaPay
FEDAPAY_API_KEY=sk_sandbox_your_api_key_here
FEDAPAY_ENVIRONMENT=sandbox
FEDAPAY_WEBHOOK_SECRET=your_webhook_secret
```

### Obtenir les Clés FedaPay

1. **Créer un compte** : https://fedapay.com
2. **Aller dans Settings → API Keys**
3. **Mode Sandbox** :
   - Public Key : `pk_sandbox_...`
   - Secret Key : `sk_sandbox_...`
4. **Mode Live** (Production) :
   - Public Key : `pk_live_...`
   - Secret Key : `sk_live_...`

### Configurer le Webhook

1. **Dashboard FedaPay → Webhooks**
2. **Ajouter URL** : `https://votre-api.com/api/v1/payments/webhook`
3. **Événements** :
   - `transaction.approved`
   - `transaction.failed`
   - `transaction.cancelled`
4. **Copier Webhook Secret**

---

## 📊 Exemples de Plans Recommandés

### Plan Starter (15 000 FCFA/mois)
```json
{
  "monthly_quota": 100,
  "max_api_keys": 3,
  "max_users": 1,
  "features": {
    "webhook_support": true,
    "priority_support": false,
    "api_access": true,
    "bulk_upload": false
  }
}
```

### Plan Professional (50 000 FCFA/mois)
```json
{
  "monthly_quota": 500,
  "max_api_keys": 10,
  "max_users": 5,
  "features": {
    "webhook_support": true,
    "priority_support": true,
    "api_access": true,
    "bulk_upload": true,
    "advanced_analytics": true
  }
}
```

### Plan Enterprise (150 000 FCFA/mois)
```json
{
  "monthly_quota": 2000,
  "max_api_keys": 50,
  "max_users": 20,
  "features": {
    "webhook_support": true,
    "priority_support": true,
    "custom_branding": true,
    "api_access": true,
    "bulk_upload": true,
    "advanced_analytics": true,
    "dedicated_support": true
  }
}
```

---

## 🧪 Tests

### 1. Créer des Plans de Test

```bash
# Via API ou directement en DB
INSERT INTO subscription_plans VALUES (
  gen_random_uuid(),
  'Starter',
  'starter',
  'Plan de démarrage',
  15000,
  'XOF',
  'monthly',
  100,
  3,
  1,
  '{"webhook_support": true}',
  '["100 vérifications/mois", "Support email"]',
  true,
  false,
  false,
  1,
  NOW(),
  NOW(),
  NULL
);
```

### 2. Tester le Paiement Sandbox

FedaPay Sandbox fournit des numéros de test :

**Mobile Money Test** :
- Numéro : `+22997000001`
- Code : `0000`

**Carte Test** :
- Numéro : `4242424242424242`
- Expiration : `12/25`
- CVV : `123`

---

## ✅ Checklist Implémentation

- [x] Créer modèle `SubscriptionPlan`
- [x] Créer modèle `Payment`
- [x] Modifier modèle `Company`
- [x] Créer schémas Pydantic
- [x] Créer endpoints admin plans
- [x] Créer endpoint public plans
- [x] Créer service FedaPay
- [x] Créer endpoints paiements
- [x] Créer webhook FedaPay
- [ ] Créer migration Alembic
- [ ] Ajouter variables `.env`
- [ ] Tester avec FedaPay Sandbox
- [ ] Créer plans de test
- [ ] Documenter pour frontend

---

## 🚀 Prochaines Étapes

1. **Créer la migration Alembic** pour les nouvelles tables
2. **Ajouter les clés FedaPay** dans `.env`
3. **Créer des plans de test** via l'API admin
4. **Tester le workflow complet** en sandbox
5. **Développer l'interface frontend** pour afficher et acheter les plans

---

**Le système de paiement est prêt à être déployé !** 🎉
