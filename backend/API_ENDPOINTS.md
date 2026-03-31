# 📚 Documentation API - KYC Platform

**Base URL**: `http://localhost:8000/api/v1`

---

## 🔐 Authentification

### Entreprises (API)
```
Authorization: Bearer sk_votre_secret_key
```

### Admins (Dashboard)
```
Authorization: Bearer jwt_token
```

---

## 📋 Endpoints Disponibles

### 1. Verifications

#### POST `/verifications/initiate`
Initier une nouvelle vérification KYC

**Headers**:
```
Authorization: Bearer sk_...
Content-Type: application/json
```

**Body**:
```json
{
  "full_name": "Jean Dupont",
  "email": "jean@example.com",
  "phone": "+33612345678",
  "country": "France",
  "external_reference": "REF-001",
  "verification_type": "document"
}
```

**Response** (201):
```json
{
  "verification_id": "KYC-2026000001",
  "verification_url": "http://localhost:3000/session/abc123...",
  "status": "pending"
}
```

#### GET `/verifications/{verification_id}`
Récupérer une vérification

**Response** (200):
```json
{
  "id": "uuid",
  "verification_id": "KYC-2026000001",
  "full_name": "Jean Dupont",
  "email": "jean@example.com",
  "status": "pending",
  "created_at": "2026-03-14T16:00:00",
  ...
}
```

#### GET `/verifications/`
Liste paginée des vérifications

**Query Params**:
- `status_filter` (optional): pending, in_review, approved, rejected
- `page` (default: 1)
- `page_size` (default: 20, max: 100)

**Response** (200):
```json
{
  "total": 10,
  "page": 1,
  "page_size": 20,
  "verifications": [...]
}
```

#### POST `/verifications/{verification_id}/review`
Valider/Rejeter une vérification (Admin uniquement)

**Body**:
```json
{
  "action": "approve",
  "rejection_reason": null
}
```

---

### 2. Companies

#### POST `/companies/register`
Inscription d'une nouvelle entreprise

**Body**:
```json
{
  "company_name": "Ma Société",
  "email": "contact@societe.com",
  "phone": "+33612345678",
  "country": "France",
  "address": "123 Rue Test",
  "rccm": "RC-123456",
  "tax_number": "FR123456789",
  "website": "https://societe.com",
  "legal_representative": "John Doe",
  "password": "motdepasse123"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "company_name": "Ma Société",
  "email": "contact@societe.com",
  "status": "sandbox",
  "is_validated": false,
  "public_key": "pk_...",
  ...
}
```

#### POST `/companies/login`
Login entreprise

**Body**:
```json
{
  "email": "contact@societe.com",
  "password": "motdepasse123"
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### GET `/companies/me`
Info entreprise connectée

#### GET `/companies/api-keys`
Récupérer les clés API

**Response**:
```json
{
  "public_key": "pk_...",
  "secret_key": "sk_...",
  "message": "Conservez votre clé secrète en lieu sûr"
}
```

#### POST `/companies/api-keys/regenerate`
Régénérer les clés API

---

### 3. Admin

#### POST `/admin/register`
Créer le premier administrateur (une seule fois)

**Body**:
```json
{
  "username": "admin",
  "email": "admin@kyc.com",
  "password": "admin123",
  "role": "super_admin"
}
```

#### POST `/admin/login`
Login administrateur

**Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### GET `/admin/companies`
Liste toutes les entreprises

**Query Params**:
- `status_filter`: sandbox, production, suspended
- `skip`: 0
- `limit`: 50 (max: 100)

#### POST `/admin/companies/{company_id}/validate`
Valider une entreprise (passe en production)

#### GET `/admin/verifications`
Liste toutes les vérifications (tous clients)

---

### 4. Session (Utilisateur Final)

#### GET `/session/{session_token}`
Récupérer les infos de la session de vérification

#### POST `/session/{session_token}/submit-documents`
Soumettre les documents

**Form Data**:
- `document_type`: passport, id_card, driver_license
- `document_number`: string
- `document_front`: file (jpg, png, webp)
- `document_back`: file (optional)
- `selfie`: file (optional)

---

## 🧪 Exemple d'Utilisation

### Python
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
SECRET_KEY = "sk_Dqm1Z5VEw0W-5MrtBvkWsoNPQ42Hbv6LWPsTJDCor7A"

headers = {"Authorization": f"Bearer {SECRET_KEY}"}

# Initier vérification
response = requests.post(
    f"{BASE_URL}/verifications/initiate",
    json={
        "full_name": "Jean Dupont",
        "email": "jean@example.com",
        "external_reference": "REF-001"
    },
    headers=headers
)

data = response.json()
print(f"Vérification créée: {data['verification_id']}")
print(f"URL: {data['verification_url']}")
```

### JavaScript
```javascript
const BASE_URL = 'http://localhost:8000/api/v1';
const SECRET_KEY = 'sk_Dqm1Z5VEw0W-5MrtBvkWsoNPQ42Hbv6LWPsTJDCor7A';

const response = await fetch(`${BASE_URL}/verifications/initiate`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${SECRET_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    full_name: 'Jean Dupont',
    email: 'jean@example.com',
    external_reference: 'REF-001'
  })
});

const data = await response.json();
console.log('Vérification:', data.verification_id);
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/verifications/initiate \
  -H "Authorization: Bearer sk_Dqm1Z5VEw0W-5MrtBvkWsoNPQ42Hbv6LWPsTJDCor7A" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jean Dupont",
    "email": "jean@example.com",
    "external_reference": "REF-001"
  }'
```

---

## 📊 Codes de Statut

- `200` - OK
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (clé API invalide)
- `403` - Forbidden (quota dépassé, compte suspendu)
- `404` - Not Found
- `410` - Gone (session expirée)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

---

## 🔄 Workflow Complet

```
1. Entreprise → POST /verifications/initiate
   ↓
2. API → Retourne verification_url
   ↓
3. Utilisateur → Ouvre verification_url
   ↓
4. Utilisateur → POST /session/{token}/submit-documents
   ↓
5. Background → Compression + Upload Cloudinary
   ↓
6. Admin → POST /verifications/{id}/review
   ↓
7. Background → Webhook vers entreprise
   ↓
8. Background → Email notification
```
