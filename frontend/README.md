# 🎨 KYC Platform - Frontend

Frontend Next.js professionnel pour la plateforme de vérification KYC.

## 🚀 Technologies

- **Next.js 14** - Framework React avec App Router
- **TypeScript** - Typage statique
- **TailwindCSS** - Styling utilitaire
- **Lucide React** - Icônes modernes
- **next-themes** - Thème sombre/clair
- **Axios** - Client HTTP

## 🎨 Design System

### Couleurs

**Thème Emerald (Principal)**
- Utilisé pour : Actions principales, succès, éléments positifs
- Couleurs : emerald-50 à emerald-950

**Thème Rose (Secondaire)**
- Utilisé pour : Erreurs, suppressions, alertes
- Couleurs : rose-50 à rose-950

**Règles**
- ❌ Pas de mélange des deux couleurs
- ❌ Pas de dégradés
- ✅ Utiliser emerald OU rose selon le contexte
- ✅ Thème sombre/clair automatique

### Composants UI

Tous les composants sont dans `src/components/ui/` :

- **Button** - Boutons avec variantes (default, destructive, outline, ghost)
- **Card** - Cartes avec header, content, footer
- **Input** - Champs de saisie stylisés
- **Badge** - Badges pour statuts

## 📁 Structure

```
frontend/
├── src/
│   ├── app/                    # Pages Next.js (App Router)
│   │   ├── page.tsx           # Page d'accueil publique
│   │   ├── layout.tsx         # Layout racine
│   │   ├── globals.css        # Styles globaux
│   │   └── company/           # Pages entreprise
│   │       ├── login/         # Connexion
│   │       ├── register/      # Inscription
│   │       └── dashboard/     # Dashboard
│   ├── components/
│   │   ├── ui/                # Composants UI de base
│   │   ├── layout/            # Navbar, Footer
│   │   └── theme-provider.tsx # Provider thème
│   ├── lib/
│   │   ├── utils.ts           # Utilitaires (cn)
│   │   └── api.ts             # Client API Axios
│   ├── types/
│   │   └── index.ts           # Types TypeScript
│   └── hooks/
│       └── useAuth.ts         # Hook authentification
├── public/                     # Assets statiques
├── tailwind.config.ts         # Config Tailwind
├── tsconfig.json              # Config TypeScript
└── package.json
```

## 🛠️ Installation

```bash
# Installer les dépendances
npm install

# Copier .env.example vers .env
cp .env.example .env

# Configurer l'URL de l'API
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 🚀 Démarrage

```bash
# Mode développement
npm run dev

# Build production
npm run build

# Démarrer en production
npm start

# Linter
npm run lint
```

Le site sera accessible sur `http://localhost:3000`

## 📄 Pages

### Pages Publiques

- **/** - Page d'accueil
  - Hero section
  - Fonctionnalités
  - Comment ça marche
  - Pricing
  - CTA

### Pages Entreprise

- **/company/login** - Connexion
- **/company/register** - Inscription
- **/company/dashboard** - Dashboard principal
  - Stats vérifications
  - Quota mensuel
  - Abonnement actuel
  - Navigation sidebar

### Pages Admin (À venir)

- **/admin/login** - Connexion admin
- **/admin/dashboard** - Dashboard admin
- **/admin/companies** - Gestion entreprises
- **/admin/plans** - Gestion plans

### Documentation (À venir)

- **/docs** - Documentation développeurs
  - Guide démarrage rapide
  - Référence API
  - Exemples de code
  - Webhooks

## 🎨 Responsive Design

Toutes les pages sont **100% responsive** :

- **Mobile** (< 768px) - Navigation hamburger, layout vertical
- **Tablet** (768px - 1024px) - Layout adaptatif
- **Desktop** (> 1024px) - Layout complet avec sidebar

## 🌓 Thème Sombre/Clair

Le thème est géré automatiquement :

```tsx
import { ThemeToggle } from '@/components/theme-toggle'

// Utiliser le composant
<ThemeToggle />
```

Le thème suit les préférences système par défaut et peut être changé manuellement.

## 🔐 Authentification

```tsx
import { useAuth } from '@/hooks/useAuth'

function ProtectedPage() {
  const { company, loading, logout } = useAuth()
  
  if (loading) return <div>Chargement...</div>
  
  return (
    <div>
      <h1>Bienvenue {company.company_name}</h1>
      <button onClick={logout}>Déconnexion</button>
    </div>
  )
}
```

## 📡 API Client

```tsx
import api from '@/lib/api'

// GET request
const response = await api.get('/verifications')

// POST request
const response = await api.post('/verifications', data)

// Le token JWT est automatiquement ajouté aux headers
```

## 🎯 Prochaines Étapes

- [ ] Dashboard admin complet
- [ ] Page de documentation développeurs
- [ ] Gestion des clés API
- [ ] Liste des vérifications
- [ ] Gestion des utilisateurs
- [ ] Paramètres entreprise
- [ ] Gestion abonnement et paiements
- [ ] Tests unitaires (Jest + React Testing Library)
- [ ] Tests E2E (Playwright)

## 📚 Documentation Complète

Pour la documentation complète de l'API backend, voir :
- `../backend/SUBSCRIPTION_PAYMENT_SYSTEM.md`
- `../backend/BACKEND_100_PERCENT.md`

## 🤝 Contribution

1. Respecter le design system (Emerald/Rose, pas de mélange)
2. Toutes les pages doivent être responsive
3. Utiliser TypeScript pour le typage
4. Suivre les conventions de nommage Next.js

## 📝 License

Propriétaire - KYC Platform 2026
