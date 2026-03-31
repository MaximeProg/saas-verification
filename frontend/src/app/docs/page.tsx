'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Book, Key, Webhook, FileText, AlertCircle, CheckCircle, ChevronRight, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'

type Section = 'introduction' | 'authentication' | 'initiate' | 'retrieve' | 'list' | 'status' | 'webhooks' | 'errors'

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState<Section>('introduction')
  const [activeLanguage, setActiveLanguage] = useState<'curl' | 'javascript' | 'python' | 'php'>('curl')

  const menuSections = [
    {
      title: 'Démarrage',
      items: [
        { id: 'introduction' as Section, label: 'Introduction', icon: Book },
        { id: 'authentication' as Section, label: 'Authentification', icon: Key },
      ]
    },
    {
      title: 'Vérifications KYC',
      items: [
        { id: 'initiate' as Section, label: '1. Initier une vérification', icon: FileText },
        { id: 'retrieve' as Section, label: '2. Récupérer une vérification', icon: CheckCircle },
        { id: 'list' as Section, label: '3. Lister les vérifications', icon: FileText },
        { id: 'status' as Section, label: '4. Vérifier le statut', icon: CheckCircle },
      ]
    },
    {
      title: 'Avancé',
      items: [
        { id: 'webhooks' as Section, label: 'Webhooks', icon: Webhook },
        { id: 'errors' as Section, label: 'Gestion des erreurs', icon: AlertCircle },
      ]
    }
  ]

  const codeExamples = {
    introduction: {
      curl: `# URL de base
https://api.kycplatform.com/api/v1

# Headers requis
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json`,
      javascript: `const API_URL = 'https://api.kycplatform.com/api/v1';
const API_KEY = 'your_api_key_here';

const headers = {
  'Authorization': \`Bearer \${API_KEY}\`,
  'Content-Type': 'application/json'
};`,
      python: `API_URL = 'https://api.kycplatform.com/api/v1'
API_KEY = 'your_api_key_here'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}`,
      php: `<?php
$apiUrl = 'https://api.kycplatform.com/api/v1';
$apiKey = 'your_api_key_here';

$headers = [
    'Authorization: Bearer ' . $apiKey,
    'Content-Type: application/json'
];`
    },
    authentication: {
      curl: `curl -X POST https://api.kycplatform.com/api/v1/auth/token \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "votre@email.com",
    "password": "votre_mot_de_passe"
  }'`,
      javascript: `const response = await fetch(\`\${API_URL}/auth/token\`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'votre@email.com',
    password: 'votre_mot_de_passe'
  })
});

const data = await response.json();
console.log('Token:', data.access_token);`,
      python: `import requests

response = requests.post(
    f'{API_URL}/auth/token',
    json={
        'email': 'votre@email.com',
        'password': 'votre_mot_de_passe'
    }
)

data = response.json()
print('Token:', data['access_token'])`,
      php: `<?php
$ch = curl_init($apiUrl . '/auth/token');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'email' => 'votre@email.com',
    'password' => 'votre_mot_de_passe'
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$data = json_decode($response, true);
echo 'Token: ' . $data['access_token'];`
    },
    initiate: {
      curl: `curl -X POST https://api.kycplatform.com/api/v1/verifications/initiate \\
  -H "Authorization: Bearer YOUR_SECRET_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+229XXXXXXXX",
    "country": "BJ",
    "external_reference": "USER-12345",
    "verification_type": "document"
  }'`,
      javascript: `const response = await fetch('https://api.kycplatform.com/api/v1/verifications/initiate', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_SECRET_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    full_name: 'John Doe',
    email: 'john@example.com',
    phone: '+229XXXXXXXX',
    country: 'BJ',
    external_reference: 'USER-12345',
    verification_type: 'document'
  })
});

const data = await response.json();
console.log('Verification ID:', data.verification_id);
console.log('Verification URL:', data.verification_url);`,
      python: `import requests

response = requests.post(
    'https://api.kycplatform.com/api/v1/verifications/initiate',
    headers={
        'Authorization': 'Bearer YOUR_SECRET_KEY',
        'Content-Type': 'application/json'
    },
    json={
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+229XXXXXXXX',
        'country': 'BJ',
        'external_reference': 'USER-12345',
        'verification_type': 'document'
    }
)

data = response.json()
print('Verification ID:', data['verification_id'])
print('Verification URL:', data['verification_url'])`,
      php: `<?php
$ch = curl_init('https://api.kycplatform.com/api/v1/verifications/initiate');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'full_name' => 'John Doe',
    'email' => 'john@example.com',
    'phone' => '+229XXXXXXXX',
    'country' => 'BJ',
    'external_reference' => 'USER-12345',
    'verification_type' => 'document'
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer YOUR_SECRET_KEY',
    'Content-Type: application/json'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$data = json_decode($response, true);

echo 'Verification ID: ' . $data['verification_id'];
echo 'Verification URL: ' . $data['verification_url'];`
    },
    retrieve: {
      curl: `curl -X GET https://api.kycplatform.com/api/v1/verifications/KYC-2026000001 \\
  -H "Authorization: Bearer YOUR_SECRET_KEY"`,
      javascript: `const response = await fetch('https://api.kycplatform.com/api/v1/verifications/KYC-2026000001', {
  headers: {
    'Authorization': 'Bearer YOUR_SECRET_KEY'
  }
});

const verification = await response.json();
console.log('Status:', verification.status);
console.log('Full Name:', verification.full_name);`,
      python: `import requests

response = requests.get(
    'https://api.kycplatform.com/api/v1/verifications/KYC-2026000001',
    headers={'Authorization': 'Bearer YOUR_SECRET_KEY'}
)

verification = response.json()
print('Status:', verification['status'])
print('Full Name:', verification['full_name'])`,
      php: `<?php
$ch = curl_init('https://api.kycplatform.com/api/v1/verifications/KYC-2026000001');
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer YOUR_SECRET_KEY'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$verification = json_decode($response, true);

echo 'Status: ' . $verification['status'];`
    },
    list: {
      curl: `curl -X GET "https://api.kycplatform.com/api/v1/verifications?page=1&page_size=20&status=approved" \\
  -H "Authorization: Bearer YOUR_SECRET_KEY"`,
      javascript: `const response = await fetch('https://api.kycplatform.com/api/v1/verifications?page=1&page_size=20&status=approved', {
  headers: {
    'Authorization': 'Bearer YOUR_SECRET_KEY'
  }
});

const data = await response.json();
console.log('Total:', data.total);
console.log('Verifications:', data.verifications);`,
      python: `import requests

response = requests.get(
    'https://api.kycplatform.com/api/v1/verifications',
    headers={'Authorization': 'Bearer YOUR_SECRET_KEY'},
    params={
        'page': 1,
        'page_size': 20,
        'status': 'approved'
    }
)

data = response.json()
print('Total:', data['total'])`,
      php: `<?php
$params = http_build_query([
    'page' => 1,
    'page_size' => 20,
    'status' => 'approved'
]);

$ch = curl_init('https://api.kycplatform.com/api/v1/verifications?' . $params);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer YOUR_SECRET_KEY'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$data = json_decode($response, true);

echo 'Total: ' . $data['total'];`
    },
    status: {
      curl: `curl -X GET https://api.kycplatform.com/api/v1/verifications/KYC-2026000001 \\
  -H "Authorization: Bearer YOUR_SECRET_KEY"`,
      javascript: `// Vérifier périodiquement le statut
const checkStatus = async (verificationId) => {
  const response = await fetch(
    \`https://api.kycplatform.com/api/v1/verifications/\${verificationId}\`,
    {
      headers: { 'Authorization': 'Bearer YOUR_SECRET_KEY' }
    }
  );
  
  const verification = await response.json();
  return verification.status;
};

// Polling (non recommandé - utilisez plutôt les webhooks)
const pollStatus = async (verificationId) => {
  const status = await checkStatus(verificationId);
  
  if (status === 'pending' || status === 'in_review') {
    setTimeout(() => pollStatus(verificationId), 30000);
  } else {
    console.log('Verification terminée:', status);
  }
};`,
      python: `import requests
import time

def check_status(verification_id):
    response = requests.get(
        f'https://api.kycplatform.com/api/v1/verifications/{verification_id}',
        headers={'Authorization': 'Bearer YOUR_SECRET_KEY'}
    )
    return response.json()['status']

# Polling (non recommandé - utilisez plutôt les webhooks)
def poll_status(verification_id):
    while True:
        status = check_status(verification_id)
        
        if status in ['pending', 'in_review']:
            time.sleep(30)
        else:
            print(f'Verification terminée: {status}')
            break`,
      php: `<?php
function checkStatus($verificationId) {
    $ch = curl_init('https://api.kycplatform.com/api/v1/verifications/' . $verificationId);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer YOUR_SECRET_KEY'
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    $data = json_decode($response, true);
    
    return $data['status'];
}

// Polling (non recommandé)
while (true) {
    $status = checkStatus('KYC-2026000001');
    
    if (in_array($status, ['pending', 'in_review'])) {
        sleep(30);
    } else {
        echo 'Verification terminée: ' . $status;
        break;
    }
}`
    },
    webhooks: {
      curl: `# Configuration du webhook
curl -X POST https://api.kycplatform.com/api/v1/webhooks \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://votre-site.com/webhook",
    "events": ["verification.completed", "verification.failed"]
  }'`,
      javascript: `// Configurer le webhook
const webhook = await fetch(\`\${API_URL}/webhooks\`, {
  method: 'POST',
  headers,
  body: JSON.stringify({
    url: 'https://votre-site.com/webhook',
    events: ['verification.completed', 'verification.failed']
  })
});

// Recevoir les événements
app.post('/webhook', (req, res) => {
  const event = req.body;
  console.log('Event:', event.type);
  console.log('Verification ID:', event.verification_id);
  res.status(200).send('OK');
});`,
      python: `# Configurer le webhook
response = requests.post(
    f'{API_URL}/webhooks',
    headers=headers,
    json={
        'url': 'https://votre-site.com/webhook',
        'events': ['verification.completed', 'verification.failed']
    }
)

# Recevoir les événements (Flask)
@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.json
    print('Event:', event['type'])
    print('Verification ID:', event['verification_id'])
    return 'OK', 200`,
      php: `<?php
// Configurer le webhook
$webhookData = [
    'url' => 'https://votre-site.com/webhook',
    'events' => ['verification.completed', 'verification.failed']
];

$ch = curl_init($apiUrl . '/webhooks');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($webhookData));
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_exec($ch);

// Recevoir les événements
$payload = file_get_contents('php://input');
$event = json_decode($payload, true);
echo 'Event: ' . $event['type'];`
    },
    errors: {
      curl: `# Exemple de réponse d'erreur
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Le champ 'document_type' est requis",
    "details": {
      "field": "document_type",
      "reason": "missing_field"
    }
  }
}`,
      javascript: `try {
  const response = await fetch(\`\${API_URL}/verifications\`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.error.message);
    console.error('Code:', error.error.code);
  }
} catch (err) {
  console.error('Network error:', err);
}`,
      python: `try:
    response = requests.post(
        f'{API_URL}/verifications',
        headers=headers,
        json=data
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as err:
    error = err.response.json()
    print('Error:', error['error']['message'])
    print('Code:', error['error']['code'])`,
      php: `<?php
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if ($httpCode >= 400) {
    $error = json_decode($response, true);
    echo 'Error: ' . $error['error']['message'];
    echo 'Code: ' . $error['error']['code'];
}`
    },
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'introduction':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-2xl font-bold">Introduction</h2>
              <p className="mb-4 leading-relaxed">
                L'API KYC Platform vous permet d'intégrer la vérification d'identité dans votre application. 
                Cette documentation vous guide à travers les différentes fonctionnalités disponibles.
              </p>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">URL de base</h3>
              <div className="rounded-lg bg-muted p-4">
                <code className="text-sm">https://api.kycplatform.com/api/v1</code>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Format des données</h3>
              <p className="mb-2 leading-relaxed">
                Toutes les requêtes et réponses utilisent le format JSON. Vous devez inclure le header suivant :
              </p>
              <div className="rounded-lg bg-muted p-4">
                <code className="text-sm">Content-Type: application/json</code>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Authentification</h3>
              <p className="leading-relaxed">
                Toutes les requêtes API nécessitent une clé API valide. Vous pouvez obtenir votre clé API 
                depuis votre dashboard après inscription. La clé doit être incluse dans le header Authorization.
              </p>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Démarrage rapide</h3>
              <ol className="list-decimal space-y-2 pl-6">
                <li>Créez un compte sur la plateforme</li>
                <li>Récupérez votre clé API depuis le dashboard</li>
                <li>Faites votre première requête API</li>
                <li>Configurez les webhooks pour recevoir les notifications</li>
              </ol>
            </div>
          </div>
        )

      case 'authentication':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-2xl font-bold">Authentification</h2>
              <p className="mb-4 leading-relaxed">
                L'API utilise des tokens JWT pour l'authentification. Vous devez d'abord obtenir un token 
                d'accès en utilisant vos identifiants.
              </p>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Obtenir un token</h3>
              <p className="mb-3 leading-relaxed">
                Endpoint : <code className="rounded bg-muted px-2 py-1 text-sm">POST /auth/token</code>
              </p>
              <div className="space-y-3">
                <div>
                  <p className="mb-2 font-medium">Paramètres requis :</p>
                  <ul className="space-y-1 pl-6">
                    <li><code className="text-sm">email</code> - Votre adresse email</li>
                    <li><code className="text-sm">password</code> - Votre mot de passe</li>
                  </ul>
                </div>
                <div>
                  <p className="mb-2 font-medium">Réponse :</p>
                  <div className="rounded-lg bg-muted p-4">
                    <pre className="text-sm">{`{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}`}</pre>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Utiliser le token</h3>
              <p className="mb-3 leading-relaxed">
                Incluez le token dans le header Authorization de toutes vos requêtes :
              </p>
              <div className="rounded-lg bg-muted p-4">
                <code className="text-sm">Authorization: Bearer YOUR_ACCESS_TOKEN</code>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Expiration du token</h3>
              <p className="leading-relaxed">
                Les tokens expirent après 1 heure. Lorsqu'un token expire, vous recevrez une erreur 401. 
                Vous devrez alors obtenir un nouveau token.
              </p>
            </div>
          </div>
        )

      case 'initiate':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-3xl font-bold">1. Initier une vérification</h2>
              <p className="mb-4 text-lg leading-relaxed text-muted-foreground">
                Créez une nouvelle demande de vérification KYC pour un utilisateur. Cette requête génère un lien unique 
                que vous devrez envoyer à votre utilisateur pour qu'il puisse soumettre ses documents.
              </p>
            </div>

            <div className="rounded-lg border-2 border-emerald-600/20 bg-emerald-50 dark:bg-emerald-950/20 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-emerald-600 p-2">
                  <FileText className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-semibold">Endpoint</p>
                  <code className="text-sm">POST /api/v1/verifications/initiate</code>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Paramètres de la requête</h3>
              <div className="overflow-hidden rounded-lg border">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Paramètre</th>
                      <th className="px-4 py-3 text-left font-semibold">Type</th>
                      <th className="px-4 py-3 text-left font-semibold">Requis</th>
                      <th className="px-4 py-3 text-left font-semibold">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    <tr>
                      <td className="px-4 py-3"><code>full_name</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3"><span className="rounded bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">Oui</span></td>
                      <td className="px-4 py-3">Nom complet de l'utilisateur</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>email</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3"><span className="rounded bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">Oui</span></td>
                      <td className="px-4 py-3">Adresse email de l'utilisateur</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>external_reference</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3"><span className="rounded bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">Oui</span></td>
                      <td className="px-4 py-3">Votre référence interne unique</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>phone</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3"><span className="rounded bg-gray-100 px-2 py-1 text-xs font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200">Non</span></td>
                      <td className="px-4 py-3">Numéro de téléphone (format international)</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>country</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3"><span className="rounded bg-gray-100 px-2 py-1 text-xs font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200">Non</span></td>
                      <td className="px-4 py-3">Code pays ISO (ex: BJ, FR, CI)</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>verification_type</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3"><span className="rounded bg-gray-100 px-2 py-1 text-xs font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200">Non</span></td>
                      <td className="px-4 py-3">Type: document, database, full (défaut: document)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Réponse de succès (201)</h3>
              <div className="rounded-lg bg-muted p-4">
                <pre className="text-sm">{`{
  "verification_id": "KYC-2026000001",
  "verification_url": "https://verify.kycplatform.com/abc123xyz",
  "session_token": "sess_abc123xyz",
  "status": "pending",
  "expires_at": "2026-03-18T10:00:00Z",
  "created_at": "2026-03-16T10:00:00Z"
}`}</pre>
              </div>
            </div>

            <div className="rounded-lg border-l-4 border-blue-600 bg-blue-50 dark:bg-blue-950/20 p-4">
              <p className="mb-2 font-semibold text-blue-900 dark:text-blue-100">💡 Étapes suivantes</p>
              <ol className="list-decimal space-y-2 pl-5 text-sm text-blue-800 dark:text-blue-200">
                <li>Envoyez le <code>verification_url</code> à votre utilisateur par email ou SMS</li>
                <li>L'utilisateur accède au lien et soumet ses documents</li>
                <li>Vous recevez une notification webhook lorsque le statut change</li>
                <li>Récupérez les détails de la vérification via l'API</li>
              </ol>
            </div>
          </div>
        )

      case 'retrieve':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-3xl font-bold">2. Récupérer une vérification</h2>
              <p className="mb-4 text-lg leading-relaxed text-muted-foreground">
                Obtenez les détails complets d'une vérification existante, incluant le statut, les documents soumis 
                et les résultats de la validation.
              </p>
            </div>

            <div className="rounded-lg border-2 border-emerald-600/20 bg-emerald-50 dark:bg-emerald-950/20 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-emerald-600 p-2">
                  <CheckCircle className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-semibold">Endpoint</p>
                  <code className="text-sm">GET /api/v1/verifications/:verification_id</code>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Paramètres d'URL</h3>
              <div className="overflow-hidden rounded-lg border">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Paramètre</th>
                      <th className="px-4 py-3 text-left font-semibold">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="px-4 py-3"><code>verification_id</code></td>
                      <td className="px-4 py-3">ID unique de la vérification (ex: KYC-2026000001)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Réponse de succès (200)</h3>
              <div className="rounded-lg bg-muted p-4">
                <pre className="text-sm">{`{
  "verification_id": "KYC-2026000001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+22997000000",
  "country": "BJ",
  "external_reference": "USER-12345",
  "status": "approved",
  "verification_type": "document",
  "document_type": "passport",
  "document_number": "AB123456",
  "document_front_url": "https://storage.../front.jpg",
  "document_back_url": "https://storage.../back.jpg",
  "selfie_url": "https://storage.../selfie.jpg",
  "reviewed_at": "2026-03-16T12:00:00Z",
  "reviewed_by": "admin@kycplatform.com",
  "rejection_reason": null,
  "created_at": "2026-03-16T10:00:00Z",
  "updated_at": "2026-03-16T12:00:00Z"
}`}</pre>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Statuts possibles</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-3 rounded-lg border p-3">
                  <span className="rounded bg-yellow-100 px-3 py-1 text-sm font-medium text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">pending</span>
                  <span className="text-sm">En attente de soumission par l'utilisateur</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg border p-3">
                  <span className="rounded bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">in_review</span>
                  <span className="text-sm">Documents soumis, en cours de validation</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg border p-3">
                  <span className="rounded bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">approved</span>
                  <span className="text-sm">Vérification approuvée</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg border p-3">
                  <span className="rounded bg-red-100 px-3 py-1 text-sm font-medium text-red-800 dark:bg-red-900 dark:text-red-200">rejected</span>
                  <span className="text-sm">Vérification rejetée</span>
                </div>
              </div>
            </div>
          </div>
        )

      case 'list':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-3xl font-bold">3. Lister les vérifications</h2>
              <p className="mb-4 text-lg leading-relaxed text-muted-foreground">
                Récupérez la liste paginée de toutes vos vérifications avec des options de filtrage par statut, 
                date et recherche.
              </p>
            </div>

            <div className="rounded-lg border-2 border-emerald-600/20 bg-emerald-50 dark:bg-emerald-950/20 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-emerald-600 p-2">
                  <FileText className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-semibold">Endpoint</p>
                  <code className="text-sm">GET /api/v1/verifications</code>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Paramètres de requête (Query params)</h3>
              <div className="overflow-hidden rounded-lg border">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Paramètre</th>
                      <th className="px-4 py-3 text-left font-semibold">Type</th>
                      <th className="px-4 py-3 text-left font-semibold">Défaut</th>
                      <th className="px-4 py-3 text-left font-semibold">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    <tr>
                      <td className="px-4 py-3"><code>page</code></td>
                      <td className="px-4 py-3">integer</td>
                      <td className="px-4 py-3">1</td>
                      <td className="px-4 py-3">Numéro de la page</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>page_size</code></td>
                      <td className="px-4 py-3">integer</td>
                      <td className="px-4 py-3">20</td>
                      <td className="px-4 py-3">Nombre de résultats par page (max: 100)</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>status</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3">-</td>
                      <td className="px-4 py-3">Filtrer par statut (pending, in_review, approved, rejected)</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3"><code>search</code></td>
                      <td className="px-4 py-3">string</td>
                      <td className="px-4 py-3">-</td>
                      <td className="px-4 py-3">Rechercher par nom, email ou référence</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Exemple de requête</h3>
              <div className="rounded-lg bg-muted p-4">
                <code className="text-sm">GET /api/v1/verifications?page=1&page_size=20&status=approved</code>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Réponse de succès (200)</h3>
              <div className="rounded-lg bg-muted p-4">
                <pre className="text-sm">{`{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "verifications": [
    {
      "verification_id": "KYC-2026000001",
      "full_name": "John Doe",
      "email": "john@example.com",
      "status": "approved",
      "created_at": "2026-03-16T10:00:00Z",
      "reviewed_at": "2026-03-16T12:00:00Z"
    },
    {
      "verification_id": "KYC-2026000002",
      "full_name": "Jane Smith",
      "email": "jane@example.com",
      "status": "in_review",
      "created_at": "2026-03-16T11:00:00Z",
      "reviewed_at": null
    }
  ]
}`}</pre>
              </div>
            </div>
          </div>
        )

      case 'status':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-3xl font-bold">4. Vérifier le statut</h2>
              <p className="mb-4 text-lg leading-relaxed text-muted-foreground">
                Surveillez l'évolution d'une vérification en temps réel. Bien que vous puissiez interroger l'API 
                périodiquement, nous recommandons fortement l'utilisation des webhooks pour une meilleure performance.
              </p>
            </div>

            <div className="rounded-lg border-2 border-yellow-600/20 bg-yellow-50 dark:bg-yellow-950/20 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-yellow-600 p-2">
                  <AlertCircle className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="mb-2 font-semibold text-yellow-900 dark:text-yellow-100">⚠️ Recommandation importante</p>
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    Le polling (interrogation répétée) de l'API consomme votre quota et peut être lent. 
                    Utilisez plutôt les <strong>webhooks</strong> pour recevoir des notifications instantanées 
                    lorsque le statut change.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Méthode 1 : Requête unique</h3>
              <p className="mb-3 text-sm text-muted-foreground">
                Utilisez l'endpoint de récupération pour vérifier le statut actuel :
              </p>
              <div className="rounded-lg bg-muted p-4">
                <code className="text-sm">GET /api/v1/verifications/KYC-2026000001</code>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Méthode 2 : Polling (non recommandé)</h3>
              <p className="mb-3 text-sm text-muted-foreground">
                Si vous devez absolument utiliser le polling, respectez ces bonnes pratiques :
              </p>
              <ul className="list-disc space-y-2 pl-6 text-sm">
                <li>Intervalle minimum : <strong>30 secondes</strong></li>
                <li>Arrêtez le polling une fois le statut final atteint (approved/rejected)</li>
                <li>Implémentez un timeout maximum (ex: 48 heures)</li>
                <li>Gérez les erreurs de rate limiting (429)</li>
              </ul>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Méthode 3 : Webhooks (recommandé) ✅</h3>
              <p className="mb-3 text-sm text-muted-foreground">
                Configurez un webhook pour recevoir des notifications automatiques :
              </p>
              <div className="space-y-3">
                <div className="rounded-lg border-l-4 border-emerald-600 bg-emerald-50 dark:bg-emerald-950/20 p-4">
                  <p className="mb-2 font-semibold text-emerald-900 dark:text-emerald-100">Avantages des webhooks</p>
                  <ul className="list-disc space-y-1 pl-5 text-sm text-emerald-800 dark:text-emerald-200">
                    <li>Notifications instantanées (&lt; 1 seconde)</li>
                    <li>Aucune consommation de quota API</li>
                    <li>Pas de latence ni de polling</li>
                    <li>Architecture événementielle moderne</li>
                  </ul>
                </div>
                <p className="text-sm">
                  Consultez la section <button onClick={() => setActiveSection('webhooks')} className="font-medium text-emerald-600 hover:underline">Webhooks</button> pour la configuration complète.
                </p>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Cycle de vie d'une vérification</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-100 text-sm font-bold text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">1</div>
                  <div>
                    <p className="font-semibold">pending</p>
                    <p className="text-sm text-muted-foreground">Lien envoyé, en attente de soumission</p>
                  </div>
                </div>
                <div className="ml-5 h-8 w-0.5 bg-border"></div>
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-800 dark:bg-blue-900 dark:text-blue-200">2</div>
                  <div>
                    <p className="font-semibold">in_review</p>
                    <p className="text-sm text-muted-foreground">Documents soumis, validation en cours</p>
                  </div>
                </div>
                <div className="ml-5 h-8 w-0.5 bg-border"></div>
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200">3</div>
                  <div>
                    <p className="font-semibold">approved / rejected</p>
                    <p className="text-sm text-muted-foreground">Décision finale rendue</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 'webhooks':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-2xl font-bold">Webhooks</h2>
              <p className="mb-4 leading-relaxed">
                Les webhooks vous permettent de recevoir des notifications en temps réel lorsque le statut 
                d'une vérification change.
              </p>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Configurer un webhook</h3>
              <p className="mb-3 leading-relaxed">
                Endpoint : <code className="rounded bg-muted px-2 py-1 text-sm">POST /webhooks</code>
              </p>
              <div className="space-y-3">
                <div>
                  <p className="mb-2 font-medium">Paramètres requis :</p>
                  <ul className="space-y-1 pl-6">
                    <li><code className="text-sm">url</code> - URL de votre endpoint webhook</li>
                    <li><code className="text-sm">events</code> - Liste des événements à écouter</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Événements disponibles</h3>
              <ul className="space-y-2 pl-6">
                <li><code className="text-sm">verification.created</code> - Vérification créée</li>
                <li><code className="text-sm">verification.processing</code> - Vérification en cours</li>
                <li><code className="text-sm">verification.completed</code> - Vérification terminée</li>
                <li><code className="text-sm">verification.failed</code> - Vérification échouée</li>
              </ul>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Format du payload</h3>
              <div className="rounded-lg bg-muted p-4">
                <pre className="text-sm">{`{
  "event": "verification.completed",
  "verification_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "verified",
  "timestamp": "2026-03-16T09:05:00Z",
  "data": {
    "confidence_score": 0.95
  }
}`}</pre>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Sécurité</h3>
              <p className="leading-relaxed">
                Chaque webhook inclut un header <code className="rounded bg-muted px-2 py-1 text-sm">X-Webhook-Signature</code> 
                que vous pouvez utiliser pour vérifier l'authenticité de la requête.
              </p>
            </div>
          </div>
        )

      case 'errors':
        return (
          <div className="space-y-6">
            <div>
              <h2 className="mb-4 text-2xl font-bold">Codes d'erreur</h2>
              <p className="mb-4 leading-relaxed">
                L'API utilise des codes HTTP standards et retourne des messages d'erreur détaillés en JSON.
              </p>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Codes HTTP</h3>
              <ul className="space-y-2 pl-6">
                <li><code className="text-sm">200</code> - Succès</li>
                <li><code className="text-sm">201</code> - Ressource créée</li>
                <li><code className="text-sm">400</code> - Requête invalide</li>
                <li><code className="text-sm">401</code> - Non authentifié</li>
                <li><code className="text-sm">403</code> - Accès refusé</li>
                <li><code className="text-sm">404</code> - Ressource non trouvée</li>
                <li><code className="text-sm">429</code> - Trop de requêtes</li>
                <li><code className="text-sm">500</code> - Erreur serveur</li>
              </ul>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Format des erreurs</h3>
              <div className="rounded-lg bg-muted p-4">
                <pre className="text-sm">{`{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Le champ 'document_type' est requis",
    "details": {
      "field": "document_type",
      "reason": "missing_field"
    }
  }
}`}</pre>
              </div>
            </div>

            <div>
              <h3 className="mb-3 text-xl font-semibold">Codes d'erreur personnalisés</h3>
              <ul className="space-y-2 pl-6">
                <li><code className="text-sm">INVALID_REQUEST</code> - Paramètres manquants ou invalides</li>
                <li><code className="text-sm">AUTHENTICATION_FAILED</code> - Token invalide ou expiré</li>
                <li><code className="text-sm">QUOTA_EXCEEDED</code> - Quota mensuel dépassé</li>
                <li><code className="text-sm">RATE_LIMIT_EXCEEDED</code> - Trop de requêtes</li>
                <li><code className="text-sm">RESOURCE_NOT_FOUND</code> - Ressource introuvable</li>
              </ul>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="flex min-h-screen flex-col overflow-x-hidden bg-background">
      {/* Header Documentation */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2 font-bold">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600">
                <span className="text-lg font-bold text-white">K</span>
              </div>
              <span className="text-xl">KYC Platform</span>
            </Link>
            <span className="text-sm text-muted-foreground">Documentation API</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
              <Home className="h-4 w-4" />
              <span>Retour au site</span>
            </Link>
            <Link href="/company/register">
              <Button size="sm">Créer un compte</Button>
            </Link>
          </div>
        </div>
      </header>
      
      <main className="flex-1 w-full max-w-full overflow-x-hidden">
        {/* Hero Section */}
        <section className="w-full border-b bg-gradient-to-b from-muted/50 to-background py-12">
          <div className="container mx-auto px-4">
            <h1 className="mb-3 text-4xl font-bold">Documentation API</h1>
            <p className="text-lg text-muted-foreground">
              Guide complet pour intégrer l'API de vérification KYC dans votre application
            </p>
          </div>
        </section>

        {/* Layout 3 colonnes */}
        <section className="w-full max-w-full py-8">
          <div className="container mx-auto px-4">
            <div className="grid gap-8 lg:grid-cols-12">
              {/* Menu vertical gauche */}
              <aside className="lg:col-span-3">
                <div className="sticky top-24 space-y-6">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Navigation</h3>
                  {menuSections.map((section, idx) => (
                    <div key={idx} className="space-y-1">
                      <h4 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        {section.title}
                      </h4>
                      {section.items.map((item) => {
                        const Icon = item.icon
                        return (
                          <button
                            key={item.id}
                            onClick={() => setActiveSection(item.id)}
                            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                              activeSection === item.id
                                ? 'bg-emerald-600 text-white font-medium'
                                : 'hover:bg-muted/50'
                            }`}
                          >
                            <Icon className="h-4 w-4 flex-shrink-0" />
                            <span className="flex-1">{item.label}</span>
                            {activeSection === item.id && (
                              <ChevronRight className="h-4 w-4" />
                            )}
                          </button>
                        )
                      })}
                    </div>
                  ))}
                </div>
              </aside>

              {/* Contenu central */}
              <div className="lg:col-span-6">
                <div className="prose prose-sm max-w-none">
                  {renderContent()}
                </div>

                {/* CTA */}
                <div className="mt-12 rounded-lg bg-muted p-6">
                  <h3 className="mb-2 text-lg font-semibold">Besoin d'aide ?</h3>
                  <p className="mb-4 text-sm text-muted-foreground">
                    Contactez notre équipe support pour toute question
                  </p>
                  <Link href="/company/register">
                    <Button>Créer un compte</Button>
                  </Link>
                </div>
              </div>

              {/* Exemples de code à droite */}
              <aside className="lg:col-span-3">
                <div className="sticky top-24 space-y-4">
                  <h3 className="text-sm font-semibold uppercase tracking-wider">Exemples de code</h3>
                  
                  {/* Sélecteur de langage */}
                  <div className="flex flex-wrap gap-2">
                    {(['curl', 'javascript', 'python', 'php'] as const).map((lang) => (
                      <button
                        key={lang}
                        onClick={() => setActiveLanguage(lang)}
                        className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                          activeLanguage === lang
                            ? 'bg-foreground text-background'
                            : 'bg-muted hover:bg-muted/80'
                        }`}
                      >
                        {lang.toUpperCase()}
                      </button>
                    ))}
                  </div>

                  {/* Code */}
                  <div className="rounded-lg bg-muted p-4">
                    <pre className="overflow-x-auto text-xs">
                      <code>{codeExamples[activeSection][activeLanguage]}</code>
                    </pre>
                  </div>
                </div>
              </aside>
            </div>
          </div>
        </section>
      </main>

      {/* Footer Documentation */}
      <footer className="w-full border-t bg-muted/30 py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <p className="text-sm text-muted-foreground">
              © 2026 KYC Platform. Tous droits réservés.
            </p>
            <div className="flex gap-6 text-sm">
              <Link href="/" className="text-muted-foreground hover:text-foreground">
                Accueil
              </Link>
              <Link href="/company/register" className="text-muted-foreground hover:text-foreground">
                S'inscrire
              </Link>
              <Link href="/company/login" className="text-muted-foreground hover:text-foreground">
                Se connecter
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
